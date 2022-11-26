from django.contrib import admin
from django.contrib.admin import ModelAdmin, SimpleListFilter, TabularInline
from django.forms import TextInput, ModelForm, Textarea, Select
from django.contrib.admin.widgets import AdminDateWidget


from import_export.admin import ExportActionModelAdmin, ImportExportMixin, ImportMixin
from import_export.resources import ModelResource

from .models import Movie, Review

#admin.site.register(Movie)
#admin.site.register(Review)


class ReviewForm(ModelForm):
    class Meta:
        widgets = {
            'added': AdminDateWidget,
            'text': Textarea(attrs={'rows': '2'}),
            'notes': Textarea(attrs={'rows': '2'})
        }

class ReviewResource(ModelResource):
    class Meta:
        model = Review

    def for_delete(self, row, instance):
        return self.fields['title'].clean(row) == ''

class ReviewAdmin(ImportExportMixin,admin.ModelAdmin):
    raw_id_fields = ()
    form = ReviewForm
    #inlines = (ReviewInline,)
    search_fields = ['movie__title']
    list_filter = ['sv','sf','special']
    fieldsets = [
        ('Aproved for',{
            'fields':['sv','sf']}),
        ('Commentaries for reviewers',{
            'fields':['text']}),
        ('Commentaries for web',{
            'fields':['notes']}),
        ('Special',{
            'fields':['special']}),
        ('Added',{
            'fields': ['added']})
    ]
    
admin.site.register(Review,ReviewAdmin)


class MovieForm(ModelForm):
    class Meta:
        widgets = {
            'genres': TextInput(attrs={'class': 'input-big'}),
            'date': AdminDateWidget(attrs={'class': 'vDateField input-small'}),
            'date_widget': AdminDateWidget,
            'textfield': Textarea(attrs={'rows': '2'}),
        }



class MovieFilter(SimpleListFilter):
    #List filter example that shows only referenced(used) values
    title = 'movie'
    parameter_name = 'movie'

    def lookups(self, request, model_admin):
        # You can use also "Country" instead of "model_admin.model"
        # if this is not direct relation
        movies = set([c.movie for c in model_admin.model.objects.all()])
        return [(c.id, c.name) for c in movies]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(movie__id__exact=self.value())
        else:
            return queryset



class ReviewInlineForm(ModelForm):
    class Meta:
        widgets = {
            'text': Textarea(
                attrs={'class': 'input-medium', 'rows': 2,
                       'style': 'width:95%'}),
            'notes': Textarea(
                attrs={'class': 'input-medium','rows': 2,
                        'style': 'width:95%'}),
            'sv': Select(attrs={'class': 'input-small'}),
            'sf': Select(attrs={'class': 'input-small'}),
            'special': Textarea(
                attrs={'class': 'input-medium','rows': 2,
                        'style': 'width:95%'}),

        }


class ReviewInline(TabularInline):
    model = Review
    form = ReviewInlineForm
    fields = ['sv','sf','author','text','notes','special','added']
    extra = 0
    verbose_name_plural = 'Reviews'
    sortable = 'order'
    suit_classes = 'suit-tab suit-tab-reviews'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'author':
            kwargs['initial'] = request.user.id
            return db_field.formfield(**kwargs)
        return super(ReviewInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )



class MovieResource(ModelResource):
    class Meta:
        model = Movie

    def for_delete(self, row, instance):
        return self.fields['title'].clean(row) == ''

class MovieAdmin(ImportExportMixin,admin.ModelAdmin):
    raw_id_fields = ()
    form = MovieForm
    inlines = (ReviewInline,)
    search_fields = ['title']
    list_filter = ['kind','genres']
    fieldsets = [
        (None,{
            'classes': ('suit-tab suit-tab-movie',),
            'fields':['manual','imdbID','tmdbID','tmdb_BASE_PATH']}),
        ('Data',{
            'classes': ('suit-tab suit-tab-movie',),
            'fields':['title','year','ratingIMDb','ratingTMDb','ratingRT','ratingMetascore','runtime','kind','genres','certification']}),
        ('Plot',{
            'classes': ('suit-tab suit-tab-movie',),
            'fields':['overview']}),
        ('Crow',{
            'classes': ('suit-tab suit-tab-movie',),
            'fields':['director','actors']}),
        ('Links',{
            'classes': ('suit-tab suit-tab-movie',),
            'fields': ['homepage','trailer','poster_path','backdrop_path']})
    ]
    
    suit_form_tabs = (('movie', 'Movie'), ('reviews', 'Reviews'))

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request):
            formset = inline.get_formset(request, obj)
            if obj:
                formset.extra = 0
            yield formset

admin.site.register(Movie,MovieAdmin)


