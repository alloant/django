from django.forms import ModelForm, Form, BooleanField, NullBooleanField, CheckboxInput, MultipleChoiceField, NullBooleanSelect, CharField, Textarea
from .models import Movie, Review
from .widgets import ToggleWidget


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        exclude = ['movie','author']
        widgets = {
                'special': Textarea(attrs={'rows':'1'})
                }

class MovieForm(ModelForm):
    class Meta:
        model = Movie
        fields = ('manual','imdbID','tmdbID','tmdb_BASE_PATH','year','title','ratingIMDb','ratingTMDb','ratingRT','ratingMetascore','runtime','kind','genres','director','actors','overview','poster_path','backdrop_path','certification','trailer')


class SearchForm(Form):
    query = CharField(label="Search",required=False,widget=Textarea(attrs={'rows':'1'}))

class MovieFilter(Form):
    f_movie = BooleanField(label="",required=False) 
    movie = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Movie','off': 'Movie'}))
    
    f_serie = BooleanField(label="",required=False) 
    serie = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Series','off': 'Series'}))
    
    f_miniserie = BooleanField(label="",required=False) 
    miniserie = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Miniseries','off': 'Miniseries'}))
    
    f_bollywood = BooleanField(label="",required=False) 
    bollywood = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Bollywood','off': 'Bollywood'}))

    f_action = BooleanField(label="",required=False) 
    action = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Action','off': 'Action','width': 120}))
    
    f_adventure = BooleanField(label="",required=False) 
    adventure = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Adventure','off': 'Adventure','width': 120}))
    
    f_animation = BooleanField(label="",required=False) 
    animation = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Animation','off': 'Animation','width': 120}))
    
    f_biography = BooleanField(label="",required=False) 
    biography = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Biography','off': 'Biography','width': 120}))
    
    f_drama = BooleanField(label="",required=False) 
    drama = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Drama','off': 'Drama','width': 120}))
    
    f_comedy = BooleanField(label="",required=False) 
    comedy = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Comedy','off': 'Comedy','width': 120}))
    
    f_documentary = BooleanField(label="",required=False) 
    documentary = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Documentary','off': 'Documentary','width': 120}))
    
    f_family = BooleanField(label="",required=False) 
    family = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Family','off': 'Family','width': 120}))
    
    f_fantasy = BooleanField(label="",required=False) 
    fantasy = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Fantasy','off': 'Fantasy','width': 120}))
    
    f_horror = BooleanField(label="",required=False) 
    horror = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Horror','off': 'Horror','width': 120}))
    
    f_music = BooleanField(label="",required=False) 
    music = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Music','off': 'Music','width': 120}))
    
    f_mystery = BooleanField(label="",required=False) 
    mystery = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Mystery','off': 'Mystery','width': 120}))
    
    f_romance = BooleanField(label="",required=False) 
    romance = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Romance','off': 'Romance','width': 120}))
    
    f_scifi = BooleanField(label="",required=False) 
    scifi = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'SciFi','off': 'SciFi','width': 120}))
    
    f_war = BooleanField(label="",required=False) 
    war = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'War','off': 'War','width': 120}))
    
    f_western = BooleanField(label="",required=False) 
    western = BooleanField(label="",initial=True,required=False,widget=ToggleWidget(options={'on':'Western','off': 'Western','width': 120}))

    years = CharField(label="Year(s)",required=False)


