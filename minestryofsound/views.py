from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from minestryofsound.models import UploadFileForm, Morceau
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect, HttpResponse
import json
from datetime import date, datetime, timedelta
from django.contrib.auth.decorators import login_required, permission_required

  

@login_required
@permission_required('minestryofsound.add_morceau')
def nouveau(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            nouveaumorceau = Morceau.objects.create(artiste = request.POST['artiste'], titre=request.POST['titre'], fichier = request.FILES['fichier'], date = request.POST['date'])
            nouveaumorceau.save()
            return HttpResponseRedirect('/associations/minestryofsound/playlist/')
    else:
        form = UploadFileForm()
    return render_to_response('minestryofsound/nouveau.html', {'form': form}, context_instance=RequestContext(request))

@login_required
def playlist(request):
    liste_morceaux = Morceau.objects.all()
    return render_to_response('minestryofsound/playlist.html', {'liste_morceaux': liste_morceaux},context_instance=RequestContext(request))

@login_required
def playlist_json(request):
    liste_morceaux = Morceau.objects.all()
    response = HttpResponse(mimetype='application/json')
    response.write(json.dumps([{
            'artiste': m.artiste,
            'titre': m.titre,
            'fichier': m.fichier.url,
            'date': str(m.date)
        } for m in liste_morceaux]))
    return response

@login_required    
def playlist_xml(request):
    response = HttpResponse(mimetype="text/xml")
    response.write('<?xml version="1.0" encoding="UTF-8"?><playlist version="1" xmlns="http://xspf.org/ns/0/"><title>MoS Playlist</title><creator>MINEStry Of Sound</creator><trackList>')
    liste_morceaux = Morceau.objects.all()
    for m in liste_morceaux:
        response.write('<track><location>'+m.fichier.url+'</location><title>'+m.titre+'</title><creator>'+m.artiste+'</creator></track>')
    response.write('</trackList></playlist>')
    return response

@login_required
def playlist_popup(request):
    return render_to_response('minestryofsound/popup.html',{},context_instance=RequestContext(request))

