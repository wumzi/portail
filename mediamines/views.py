# -*- coding: utf-8 -*-
from mediamines.models import Photo, Gallery
from trombi.models import UserProfile
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage
import json



@login_required
def albums_recents(request):
    latest = Gallery.objects.filter(is_public=True)
    if request.user.get_profile().en_premiere_annee():  
        latest = latest.exclude(is_hidden_1A = True)
    latest = latest[:6]
    return render_to_response('mediamines/gallery_archive.html',{'latest':latest},context_instance=RequestContext(request))
    
@login_required
def albums_liste(request, page):
    queryset = Gallery.objects.filter(is_public=True)
    if request.user.get_profile().en_premiere_annee():
        queryset = queryset.exclude(is_hidden_1A = True)
    
    
    paginator = Paginator(queryset, 6, allow_empty_first_page=True)
    if not page:
        page = request.GET.get('page', 1)
    try:
        page_number = int(page)
    except ValueError:
        if page == 'last':
            page_number = paginator.num_pages
        else:
            # Page is not 'last', nor can it be converted to an int.
            raise Http404
    try:
        page_obj = paginator.page(page_number)
    except InvalidPage:
        raise Http404
    c = RequestContext(request, {
        'object_list' : page_obj.object_list,
        'paginator': paginator,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),

        # Legacy template context stuff. New templates should use page_obj
        # to access this instead.
        'results_per_page': paginator.per_page,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'page': page_obj.number,
        'next': page_obj.next_page_number(),
        'previous': page_obj.previous_page_number(),
        'first_on_page': page_obj.start_index(),
        'last_on_page': page_obj.end_index(),
        'pages': paginator.num_pages,
        'hits': paginator.count,
        'page_range': paginator.page_range,
    }, None)
    
    
    return render_to_response("mediamines/gallery_list.html",c)

@login_required
def album_mosaique(request, slug):
    album = get_object_or_404(Gallery, title_slug = slug, is_public=True)
    if request.user.get_profile().en_premiere_annee():
        if album.is_hidden_1A:
            album = None
    return render_to_response('mediamines/gallery_detail_mosaique.html',{'album':album},context_instance=RequestContext(request))    

@login_required
def album_panorama(request, slug):
    album = get_object_or_404(Gallery, title_slug = slug, is_public=True)
    liste_eleves = UserProfile.objects.order_by('-promo','last_name')
    first_slide = request.GET.get('slide', 1)
    autoplay = request.GET.get('autoplay', 1)
	
    if request.user.get_profile().en_premiere_annee():
        if album.is_hidden_1A:
            album = None
	
    return render_to_response('mediamines/gallery_detail_panorama.html',{'album':album, 'liste_eleves':liste_eleves, 'first_slide':first_slide, 'autoplay':autoplay},context_instance=RequestContext(request))    

@login_required
#Identifier un eleve a une photo
def identifier(request, slug):
    response = HttpResponse()        
    if request.POST:
        photo = get_object_or_404(Photo, title_slug = slug)
        eleve = get_object_or_404(UserProfile, user__username = request.POST['username'])        
        photo.identifier(eleve)
        response.write('post ' + slug)
    return response

@login_required
#Desidentifier un eleve d'une photo
def desidentifier(request, slug):
    response = HttpResponse()        
    if request.POST:
        photo = get_object_or_404(Photo, title_slug = slug)
        if request.POST.get('username'):
            eleve = get_object_or_404(UserProfile, user__username = request.POST['username'])
            photo.desidentifier(eleve)
        else:
            photo.eleves.clear()
        response.write('post ' + slug)
    return response

@login_required
#La liste (format JSON) des eleves identifies sur une photo
def identifications(request, slug):
    response = HttpResponse()        
    photo = get_object_or_404(Photo, title_slug = slug)
    response.write(json.dumps([{
        'username': e.user.username            
    } for e in photo.eleves.all()]))
    return response
    
def albums_json(request):
    response = HttpResponse()        
    from django.core import serializers
    data = serializers.serialize("json", Gallery.objects.all(), indent=4, fields=('title','photos'), use_natural_keys=True)
    response.write(data.replace('\\/','/'))
    return response