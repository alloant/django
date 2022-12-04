from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, F

from datetime import datetime, timedelta

from .forms import MovieForm, ReviewForm, MovieFilter, SearchForm
from .scripts.imdbMovies import updateIMDbData, updateAllMoviesIMDb, getIMDbData, importReviews, updateRatings, updateMovieTMDb, updateOMDbRatings, updateRT

from imdb import IMDb

from el_pagination.decorators import page_template

import tmdbsimple as tmdb
tmdb.API_KEY = '3315b151d95796f817a164d4d79cdada'

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def kindsFromFilter(filter):
    r = []
    kinds = ['serie','movie','miniserie']
    cont = 0
    for k in kinds:
        if filter['f_'+k]:
            r.append(k)
            cont += 1

    if cont == len(kinds):
        return []
    else:
        return r

def genresFromFilter(filter):
    r = []
    genres = ['action','adventure','animation','biography','drama','comedy','documentary','family','fantasy','horror','music','mystery','romance','scifi','war','western']
    
    for g in genres:
        if filter['f_'+g]:
            r.append(g)
            if g == 'scifi': r[-1] = 'Science Fiction'
            if not filter[g]: r[-1] = "-" + r[-1]

    return r

def contextToFilter(rGET):
    r = {}

    if 'g' in rGET:
        fg = rGET['g']
        genres = ['action','adventure','animation','biography','drama','comedy','documentary','family','fantasy','horror','music','mystery','romance','scifi','war','western']
        for g in genres:
            kg = g
            if g == 'scifi':  kg = 'Science Fiction'

            if kg in fg or '-'+kg in fg:
                r['f_'+g] = True
            else:
                r['f_'+g] = False

            if '-'+kg in fg:
                r[g] = False
            else:
                r[g] = True

    if 'years' in rGET:
        r['years'] = rGET['years']

    if 'k' in rGET:
        fk = rGET['k']
        if isinstance(fk,str): fk = [fk]
    else:
        fk = ''

    kinds = ['serie','movie','miniserie']
    for k in kinds:
        if k in fk or fk == '':
            r['f_'+k] = True
        else:
            r['f_'+k] = False

    return r



def getFilterReviews(sec='',r='',rGET = {}):

    ## Order of movies
    order = ['-movie__year','movie__title','-movie__rating']

    if 'ord' in rGET:
        if rGET['ord'] == 'title':
            order = ['movie__title','-movie__year','-movie__ratingIMDb']
        elif rGET['ord'] == 'rating':
            order = ['-movie__ratingIMDb','-movie__year','movie__title']
        elif rGET['ord'] == 'year-rating':
            order = ['-movie__year','-movie__ratingIMDb','movie__title']
        elif rGET['ord'] == 'ratingRT':
            order = ['-movie__ratingRT','-movie__year','movie__title']
        elif rGET['ord'] == 'year-ratingRT':
            order = ['-movie__year','-movie__ratingRT','movie__title']

    ## Filter r and sec
    reviews = Review.objects.filter(Q(author__username='desr'+r))
    if sec == 'sv':
        reviews = reviews.filter(Q(sv__gte=1))
    elif sec == 'sf':
        reviews = reviews.filter(Q(sf__gte=1))


    ## Filter by years
    if 'years' in rGET:
        y  = rGET['years']
        if y.isdigit():
            reviews = reviews.filter(Q(movie__year = y))
        elif y[0] == '<' and y[1:].isdigit():
            reviews = reviews.filter(Q(movie__year__lte = y[1:]))
        elif y[0] == '>' and y[1:].isdigit():
            reviews = reviews.filter(Q(movie__year__gte = y[1:]))
        elif '-' in y:
            yy = y.split('-')
            reviews = reviews.filter(Q(movie__year__gte = yy[0]))
            reviews = reviews.filter(Q(movie__year__lte = yy[1]))



    ## Filter for esp
    if 'esp' in rGET:
        if rGET['esp'] == 'working' and sec == 'desr':
            reviews = reviews.filter(Q(sv=-1) | Q(sf=-1))    
        elif rGET['esp'] == 'other' and sec == 'desr':
            reviews = Review.objects.raw("select * from reviews_movie, reviews_review where reviews_review.movie_id = reviews_movie.imdbID group by reviews_movie.imdbID")
        elif rGET['esp'] == 'updateerrors' and sec == 'desr':
            #reviews = reviews.filter(Q(movie__ratingRT=''))
            #reviews = reviews.filter(Q(movie__ratingMetascore=0))

            reviews = reviews.filter(Q(movie__kind='movie')).order_by('movie__updated','-movie__year')
            #reviews = reviews.filter(Q(movie__kind='movie'),Q(movie__year=2021)).order_by('movie__updated','-movie__year')
            import time
            for i,r in enumerate(reviews):
                updateOMDbRatings(r.movie)
                updateRT(r.movie)
                r.movie.updated = timezone.now().date()
                r.movie.save()
                print(i)
                time.sleep(15)

                #if i > 50:
                #    break

        elif rGET['esp'] == 'editedmovies' and sec == 'desr':
            reviews = reviews.filter(Q(sv=1) | Q(sf=1))
        elif rGET['esp'] == "new":
            lt_date = Review.objects.latest('added').added - timedelta(days=20)
            reviews = reviews.filter(Q(added__gte=lt_date))
        elif rGET['esp'] == "bollywood":
            reviews = reviews.filter(Q(special__icontains='bollywood'))


    ## Filter for k
    if 'k' in rGET:
        if not ('serie' in rGET['k'] and 'movie' in rGET['k']):
            kinds = ''
            if 'serie' in rGET['k']:
                kinds = 'tv'
            elif 'movie' in rGET['k']:
                kinds = 'movie'

            if kinds:
                reviews = reviews.filter(Q(movie__kind__icontains=kinds))

    ## Filter for g
    if 'g' in rGET:
        if rGET['g']:
            for gn in rGET['g'].split(","):
                if gn[0] == '-':
                    reviews = reviews.filter(~Q(movie__genres__icontains=gn[1:]))
                else:
                    reviews = reviews.filter(Q(movie__genres__icontains=gn))

    ## Filter for act
    if 'act' in rGET:
        if rGET['act']:
            reviews = reviews.filter(Q(movie__actors__icontains=rGET['act']) | Q(movie__director__icontains=rGET['act']))

    ## Filter for q
    if 'q' in rGET:
        reviews = reviews.filter(Q(movie__title__iregex=r'%s' % (rGET['q'])))
    
    return reviews.order_by(order[0],order[1],order[2])


def edit_movie(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == "POST":
        form = MovieForm(request.POST, instance=movie)
        if form.is_valid():
            movie = form.save(commit=False)
            #post.author = request.user
            movie.updated = timezone.now()
            movie.save()
            #return redirect('listMovies')
    else:
        form = MovieForm(instance=movie)
    return render(request, 'movies/editMovie.html', {'form': form})

def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.save()
            #return redirect('listMovies')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'movies/editReview.html', {'form': form})




def get_filter(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = MovieFilter(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = MovieFilter()

    return render(request, 'movies/filter.html', {'form': form})


def getValueDict(d,k):
    if k in d:
        if d[k] == None:
            return ''
        else:
            return d[k]
    else:
        return ''

class movieClass():
    def __init__(self,imdbID = 0,tmdbID = 0, title = '', poster_path = '',backdrop_path='',year = 0,kind = "",overview = '',actors='',director='',BASE_PATH=''):
        self.imdbID = imdbID
        self.tmdbID = tmdbID
        self.title = title
        self.poster_path = poster_path
        self.backdrop_path = backdrop_path
        self.year = year
        self.kind = kind
        self.overview = overview
        self.actors = actors
        self.director = director
        self.BASE_PATH = BASE_PATH
        

@staff_member_required
def addNewMovie(request):
    add = request.GET.get("add")
    addBP = request.GET.get("addBP")
    approved = False
    if add == None:
        add = request.GET.get("approved")
        approved = True

    added = None
    if add != None:
        print("addind movie")
        movie = Movie()
        movie.tmdbID =int(add)
        movie.tmdb_BASE_PATH = addBP
        updateMovieTMDb(movie)
        
        if True:
            #mv.save()
            review = Review()
            review.author_id = request.user.username
            review.movie_id = movie.id
            if approved:
                review.sv = 2
                review.sf = 2
            else:
                review.sv = -1
                review.sf = -1

            review.save()
            added = movie.title
            #return redirect('editMovie', pk=movie.pk)

    q = request.GET.get("q")
    movies = []

    if q != None:
        if q[:6] == 'movie=':
            m = tmdb.Movies(q[6:])
            response = m.info()
            
            movies.append(movieClass(tmdbID=m.id,title=m.title,poster_path=m.poster_path,backdrop_path=m.backdrop_path,year=m.release_date[:4],kind='movie',overview=m.overview,BASE_PATH=m.BASE_PATH))
        elif q[:3] == 'tv=':
            m = tmdb.TV(q[3:])
            response = m.info()
            
            movies.append(movieClass(tmdbID=m.id,title=m.name,poster_path=m.poster_path,backdrop_path=m.backdrop_path,year=m.first_air_date[:4],kind='tv',overview=m.overview,BASE_PATH=m.BASE_PATH))
        else:
            ms = tmdb.Search()
            r1 = ms.movie(query=q)
            for r in ms.results: r['BASE_PATH'] = 'movie'
            ss = tmdb.Search()
            r2 = ss.tv(query=q)
            for r in ss.results: r['BASE_PATH'] = 'tv'

            results = ms.results + ss.results
            mvs = sorted(results, key=lambda k: k['popularity'], reverse=True)
        
            for m in mvs:
                if m['BASE_PATH'] == 'movie':
                    movies.append(movieClass(tmdbID=getValueDict(m,'id'),title=getValueDict(m,'title'),poster_path=getValueDict(m,'poster_path'),backdrop_path=getValueDict(m,'backdrop_path'),year=getValueDict(m,'release_date')[:4],kind='movie',overview=getValueDict(m,'overview'),BASE_PATH=m['BASE_PATH']))
                else:
                    movies.append(movieClass(tmdbID=getValueDict(m,'id'),title=getValueDict(m,'name'),poster_path=getValueDict(m,'poster_path'),backdrop_path=getValueDict(m,'backdrop_path'),year=getValueDict(m,'first_air_date')[:4],kind='tv',overview=getValueDict(m,'overview'),BASE_PATH=m['BASE_PATH']))
 
    if request.user_agent.is_mobile:
        tmpl = 'movies/searchMovieMobile.html'
    else:
        tmpl = 'movies/searchMovieComputer.html'
    
    return render(request,tmpl , {'movies': movies,'q':q,'added':added,'sec':'desr'})



@staff_member_required
def adminAddMovie(request):
    add = request.GET.get("add")
    approved = False
    if add == None:
        add = request.GET.get("approved")
        approved = True

    added = None
    if add != None:
        print("addind movie")
        movie = Movie()
        movie.imdbID = "tt" + add
        mv = getIMDbData(movie)

        if mv != "ERROR":
            mv.save()
            review = Review()
            review.author_id = request.user.username
            review.movie_id = movie.imdbID
            if approved:
                review.sv = 2
                review.sf = 2
            else:
                review.sv = -1
                review.sf = -1

            review.save()
            added = mv.title
            #return redirect('editMovie', pk=movie.pk)

    q=request.GET.get("q")
    movies = []

    if q != None:
        mvs = IMDb().search_movie(q)
        for m in mvs:
            movies.append(movieClass(tmdbID=m.movieID,title=m.get('title'),poster_path=m.get('cover url'),year=m.get('year'),kind=m.get('kind')))

    return render(request, 'admin/search.html', {'movies': movies,'q':q,'added':added,'sec':'desr'})


@login_required
@page_template('movies/listMovies_page.html')
def listMovies(request,template="movies/listMovies.html",page_template="movies/listMovies_page.html",extra_context=None):
    update = request.GET.get("update")
    updated = None
    if update != None:
        movie = get_object_or_404(Movie, pk=update)
        updateMovieTMDb(movie)
        updated = movie.title
   

    groups = request.user.groups.values_list('name',flat = True)
    if request.user.username == 'admin':
        sec = 'desr'
        r = 'Ind'

    for g in groups:
        if g == 'desr':
            sec = 'desr'
        elif g == 'sv' or g == 'sf':
            sec = g
        else:
            r = g

    rGET = request.GET.copy()
   
    if request.method == 'POST':
        if 'query' in request.POST:
            queryForm = SearchForm(request.POST)
            if queryForm.is_valid():
                rGET['q'] = queryForm.cleaned_data['query']
        else:
            filter = MovieFilter(request.POST)
            if filter.is_valid():
                rGET['k'] = ",".join(kindsFromFilter(filter.cleaned_data))
                rGET['g'] = ",".join(genresFromFilter(filter.cleaned_data))
                if filter.cleaned_data['years']: rGET['years'] = filter.cleaned_data['years']
                
        return redirect('/?' + rGET.urlencode())
    else:
        if 'q' in rGET and request.user_agent.is_mobile:
            queryForm = SearchForm(initial=rGET['q'])
        else:
            queryForm = SearchForm()

        if not 'query' in request.POST:
            #if 'g' in rGET or 'years' in rGET or 'k' in rGET:
            filter = MovieFilter(initial=contextToFilter(rGET))
            #else:
            #    filter = MovieFilter()

    reviews = getFilterReviews(sec=sec,r=r,rGET=rGET)

    context = {'reviews': reviews,'sec':sec,'updated':updated,'genres':g,'form':filter,'query':queryForm}
    
    if extra_context is not None:
        context.update(extra_context)

    if is_ajax(request):
        template = page_template

    return render(request,template,context)

@login_required
def updateMovie(request,pk):
    movie = get_object_or_404(Movie, pk=pk)
    groups = request.user.groups.values_list('name',flat = True)
    if request.user.username == 'admin':
        sec = 'desr'
        r = 'Ind'

    for g in groups:
        if g == 'desr':
            sec = 'desr'
        elif g == 'sv' or g == 'sf':
            sec = g
        else:
            r = g
    print("update")

    updateIMDbData(movie)
    #updateAllMoviesIMDb()
    return render(request, 'movies/detailMovie.html', {'movie': movie,'sec':sec})


