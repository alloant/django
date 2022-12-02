from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import date


class Movie(models.Model):
    manual = models.BooleanField(default=False)
    imdbID = models.CharField(max_length=10)
    tmdbID = models.IntegerField(default=0,blank=True)
    tmdb_BASE_PATH = models.CharField(max_length=20,default='',blank=True)

    year = models.PositiveSmallIntegerField(default=0)
    
    #release_date = models.DateField(default=date.today,blank=True)
    title = models.CharField(max_length=200,default='')
    
    ratingIMDb = models.DecimalField(max_digits=3,decimal_places=1,blank=True,default=0)
    ratingTMDb = models.DecimalField(max_digits=3,decimal_places=1,blank=True,default=0)
    ratingRT = models.DecimalField(max_digits=3,decimal_places=0,blank=True,default=-1)
    audienceRT = models.DecimalField(max_digits=3,decimal_places=0,blank=True,default=-1)
    #ratingRT = models.CharField(max_length=10,blank=True,default="")
    ratingMetascore = models.DecimalField(max_digits=3,decimal_places=0,blank=True,default=0)
    tomatoURL = models.URLField(default='',blank=True)
    
    certification = models.CharField(max_length=200,default='',blank=True)
    
    runtime = models.IntegerField(default=0,blank=True)
    kind = models.CharField(max_length=200,default='',blank=True)
    genres = models.CharField(max_length=200,default='',blank=True)
    director = models.CharField(max_length=500,default='',blank=True)
    actors = models.TextField(default='',blank=True)
    
    overview = models.TextField(default='',blank=True)
    
    original_language = models.CharField(max_length=200,default='',blank=True)
    original_country = models.CharField(max_length=200,default='',blank=True)
    
    tv_type = models.CharField(max_length=200,default='',blank=True)
    
    poster_path = models.CharField(max_length=200,default='',blank=True)
    backdrop_path = models.CharField(max_length=200,default='',blank=True)

    trailer = models.CharField(max_length=200,default='',blank=True)
    homepage = models.URLField(default='',blank=True)
    

    updated = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-year','title')

    def __str__(self):
        return self.title

TYPE_CHOICES = ((-1, 'Pending'), (0, 'Rejected'), (1, 'Edited'), (2, 'Approved'))

class Review(models.Model):
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,to_field='username')
    text = models.TextField(default='',blank=True,help_text='Comments only for ders')
    notes = models.TextField(default='',blank=True,help_text='Comments for everyone')
    added = models.DateTimeField(default=timezone.now)
    sv = models.SmallIntegerField(choices=TYPE_CHOICES,default=-1) # -1 pending, 0 rejected, 1 edited, 2 good
    sf = models.SmallIntegerField(choices=TYPE_CHOICES,default=-1) # -1 pending, 0 rejected, 1 edited, 2 good

    order = models.PositiveIntegerField(default=0)
    special = models.TextField(default='',blank=True,help_text='To select the movie in one special list, like Bollywood')
    class Meta:
        ordering = ('order',)

    def __str__(self):
        return "%s-%s" % (self.author,self.movie.title)

    def __unicode__(self):
        return self.name
