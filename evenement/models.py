from django.db import models
from trombi.models import UserProfile
from association.models import Association
from datetime import date, datetime, timedelta

# Create your models here.
class Evenement(models.Model):
	is_personnel = models.BooleanField()
	createur = models.ForeignKey(UserProfile, blank=True, null=True)
	association = models.ForeignKey(Association, blank=True, null=True)
	titre = models.CharField(max_length=300)
	description =  models.TextField()
	date_debut = models.DateTimeField(default=datetime.now(), blank=True)
	date_fin = models.DateTimeField(default=datetime.now(), blank=True)
	#date_post = models.DateTimeField(default=datetime.now(), blank=True)
	lieu = models.CharField(max_length=300, blank = True)
	participants = models.ManyToManyField(UserProfile,related_name='evenement_participant', blank=True)
	is_billetterie = models.BooleanField()
	billetterie = models.ForeignKey('Billetterie', related_name='bloui', null = True, blank=True)
	
	def __unicode__(self):
		return self.titre
	
	def auteur(self):
		if self.is_personnel:
			return self.createur.user.username
		else:
			return self.association.nom

	def peut_modifier(self, eleve_user):
		return (eleve_user.id == self.createur.user.id)

class Reservation(models.Model):
	eleve = models.ForeignKey(UserProfile)
	acceptee = models.BooleanField()
	
	def __unicode__(self):
		return self.titre
	

	
class Billetterie(models.Model):
	evenement = models.ForeignKey('Evenement', related_name='bla', null=True)
	prix = models.IntegerField()	
	reservations = models.ManyToManyField(Reservation,related_name='+', blank=True)
	date_fin_reservation = models.DateTimeField(default=datetime.now(), blank=True)
	nombre_places_total = models.IntegerField()
	
	def __unicode__(self):
		return self.evenement.titre
	
