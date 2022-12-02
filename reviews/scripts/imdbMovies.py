from reviews.models import Movie, Review
from imdb import IMDb
from datetime import datetime
from django.db.models import Q
from django.utils import timezone

import csv

import tmdbsimple as tmdb
tmdb.API_KEY = '3315b151d95796f817a164d4d79cdada'

from omdb import OMDBClient
oa = OMDBClient(apikey='9a67395f')


def nonull(value):
    if value == None:
        return ''
    else:
        return value

def nonullint(value):
    if value == None:
        return 0
    else:
        return value

def updateMovieTMDb(movie):
    if not movie.manual:
        print('\033[1m{:10s}\033[0m'.format("\nGetting movie: {} ({}) {}".format(movie.title,movie.imdbID,movie.updated)))
        missing = []
        if movie.tmdbID > 0:
            if movie.tmdb_BASE_PATH == 'movie':
                m = tmdb.Movies(movie.tmdbID)
            else:
                m = tmdb.TV(movie.tmdbID)
        else:
            find = tmdb.Find(movie.imdbID)
            response = find.info(external_source='imdb_id')
            if find.movie_results:
                m = find.movie_results[0]
                movie.tmdbID = m['id']
                movie.tmdb_BASE_PATH = 'movie'
                m = tmdb.Movies(m['id'])
            elif find.tv_results:
                m = find.tv_results[0]
                movie.tmdbID = m['id']
                movie.tmdb_BASE_PATH = 'tv'
                m = tmdb.TV(m['id'])
            else:
                missing.append('error')

        if not 'error' in missing:
            r = m.info()
            ex = m.external_ids()
            cr = m.credits()
    
            if 'imdb_id' in ex:
                movie.imdbID = nonull(m.imdb_id)
    
            movie.tmdb_BASE_PATH = nonull(m.BASE_PATH)
            movie.kind = nonull(m.BASE_PATH)

        
            if m.BASE_PATH == 'movie':
                movie.title = nonull(m.title)
                rdate = m.release_date
            elif m.BASE_PATH == 'tv':
                movie.title = nonull(m.name)
                rdate = m.first_air_date

            movie.year = rdate[:4]
            if movie.year == '': movie.year = 0
        
            if 'runtime' in r:
                movie.runtime = nonullint(m.runtime)
            else:
                if m.BASE_PATH == 'movie':
                    missing.append('runtime')

            genres = ""
            for g in m.genres:
                if genres: genres += ", "
                genres += g['name']
            movie.genres = genres
  
            if m.BASE_PATH == 'movie':
                cert = {}
                for c in m.releases()['countries']:
                    if c['iso_3166_1'] in ['US','IN','LK'] and c['certification'] != '':
                        cert[c['iso_3166_1']] = c['certification'].replace(' %s' % (c['iso_3166_1']),'')
                    
                scert = ''
                for c in cert:
                    if scert: scert += ","
                    scert += '%s: %s' % (c,cert[c]) 
                movie.certification = scert


            if 'overview' in r:
                movie.overview = nonull(m.overview)
                if movie.overview == '': missing.append('overview')
            else:
                missing.append('overview')

            if 'original_language' in r: movie.original_language = nonull(m.original_language)
            if 'poster_path' in r:
                movie.poster_path = nonull(m.poster_path)
                if movie.poster_path == '': missing.append('poster_path')
            else:
                missing.append('poster_path')

            if 'backdrop_path' in r: movie.backdrop_path = nonull(m.backdrop_path)

            if 'vote_average' in r: movie.ratingTMDb = nonullint(m.vote_average)
        
            if 'homepage' in r: movie.homepage = nonull(m.homepage)

            if 'type' in r: movie.tv_type = nonull(m.type)
   
            cast = ""
            if 'cast' in cr:
                for i,actor in enumerate(m.cast):
                    if cast: cast += ", "
                    cast += actor['name']
                    if i > 9: break
                movie.actors = cast
            else:
                missing.append('actors')

            crew = ""
            if 'crew' in cr:
                for c in m.crew:
                    if c['job'] == "Director":
                        if crew: crew += ", "
                        crew += c['name']
                movie.director = crew
            else:
                missing.append('actors')

            for v in m.videos()['results']:
                if v['type'].lower() == 'trailer' and v['site'].lower() == 'youtube' and v['iso_639_1'] == 'en':
                    movie.trailer = nonull(v['key'])
                    break
        ### Provisional
        if missing:
            getIMDbData(movie,missing)

        updateOMDbRatings(movie)
    
        movie.updated = timezone.now().date()
        movie.save()

def updateOMDbRatings(movie):
    print(movie.title,movie.updated)
    m = oa.get(imdbid=movie.imdbID) 
    if 'ratings' in m:
        for r in m['ratings']:
            if r['source'] == 'Rotten Tomatoes':
                if r['value'] != 'N/A':
                    movie.ratingRT = int(r['value'].replace('%',''))
                else:
                    movie.ratingRT = ''
        
        if 'metascore' in m:
            if m['metascore'] != 'N/A':
                movie.ratingMetascore = m['metascore']
            else:
                movie.ratingMetascore = 0

        if 'imdb_rating' in m:
            if m['imdb_rating'] != 'N/A':
                movie.ratingIMDb = m['imdb_rating']


def updateRatings(movie):
    print("Updating ratings...")
    updateOMDbRatings(movie)

    if movie.tmdbID > 0:
        if movie.tmdb_BASE_PATH == 'movie':
            mv = tmdb.Movies(movie.tmdbID)
        else:
            mv = tmdb.TV(movie.tmdbID)
        m = mv.info()
    else:
        find = tmdb.Find(movie.imdbID)
        response = find.info(external_source='imdb_id')
        found = False
        if find.movie_results:
            m = find.movie_results[0]
            movie.tmdb_BASE_PATH = 'movie'
            found = True
        elif find.tv_results:
            m = find.tv_results[0]
            movie.tmdb_BASE_PATH = 'tv'
            found = True
        if found:
            if 'id' in m:
                movie.tmdbID = m['id']
            else:
                movie.tmdbID = -1
     
            if 'poster_path' in m:
                if m['poster_path'] != None:
                    movie.poster_path = m['poster_path']
            if 'backdrop_path' in m:
                if m['backdrop_path'] != None:
                    movie.backdrop_path = m['backdrop_path']
            if 'vote_average' in m:
                if m['vote_average'] != None:
                    movie.ratingTMDb = m['vote_average']

    movie.updated = timezone.now().date()
    
    movie.save()

def findTMDbID(imdbID):
    find = tmdb.Find(imdbID)
    response = find.info(external_source='imdb_id')
    if find.movie_results:
        r = find.movie_results[0]
        return [r['id'],'movie',r['poster_path'],r['backdrop_path'],r['vote_average']]
    elif find.tv_results:
        r = find.tv_results[0]
        return [r['id'],'tv',r['poster_path'],r['backdrop_path'],r['vote_average']]
    else:
        return [-1,'','','']


def updateAllMoviesIMDb():
    for movie in Movie.objects.filter(Q(countries='')).order_by('updated'):
        updateIMDbData(movie)

def peopleToPlain(values):
    r = ""
    if isinstance(values, list):
        for v in values:
            if len(r) > 0: r += ", "
            r += v['name']

    return r

def getIMDbData(movie,missing):
    print("Getting from IMDb...",movie.title,missing)
    ia = IMDb() # by default access the web.
    found = False
    try:
        print("getting:",'%s' % movie.imdbID[2:])
        mv = ia.get_movie('%s' % movie.imdbID[2:])
        series = False
        if mv.get('year') > 0:
            found = True
            if 'serie' in mv.get('kind'):
                ia.update(mv,'episodes')
                series = True
    except:
        print("ERROR")
        return "ERROR"

    if found:
        if mv.get('year') != None and ('year' in missing or 'error' in missing):
            movie.year = nonullint(mv.get('year'))

        if mv.get('title') != None and ('title' in missing or 'error' in missing):
            movie.title = nonull(mv.get('title'))

        if mv.get('rating') != None and ('ratingIMDb' in missing or 'error' in missing):
            movie.ratingIMDb = nonull(mv.get('rating'))

        if isinstance(mv.get('runtime'), list) and ('runtime' in missing or 'error' in missing):
            movie.runtime = nonullint(mv.get('runtime')[0])
    
        if 'kind' in missing or 'error' in missing:
            movie.kind = nonull(mv.get('kind'))

        if isinstance(mv.get('genres'), list) and ('genres' in missing or 'error' in missing):
            movie.genres = ", ".join(mv.get('genres'))

        if 'director' in missing or 'error' in missing: 
            movie.director = peopleToPlain(mv.get('director'))
        
        if 'actors' in missing or 'error' in missing:
            movie.actors = peopleToPlain(mv.get('actors'))


        if mv.get('plot outline') != None and ('overview' in missing or 'error' in missing):
            movie.overview = nonull(mv.get('plot outline'))

        if isinstance(mv.get('plot'), list) and ('overview' in missing or 'error' in missing) and movie.overview == '':
            movie.overview = nonull(mv.get('plot')[0].split('::')[0])

        if mv.get('cover url') != None and ('poster_path' in missing or 'error' in missing):
            movie.poster_path = nonull(mv.get('cover url'))

        pg = ''
        if isinstance(mv.get('certificates'), list) and ('certificates' in missing or 'error' in missing):
            for c in mv.get('certificates'):
                if 'United States' in c:
                    if len(pg)>0: pg+=','
                    pg += c.split(':')[1]
            
            if pg: movie.certification = "US:" + pg

def updateIMDbData(movie):
    print('\033[1m{:10s}\033[0m'.format("\nGetting movie: %s (%s)" % (movie.title,movie.imdbID)))
    mv = getIMDbData(movie)
    if mv != "ERROR":
        mv.save()
        print("updated")

def importReviews():
    print("Importing reviews and movies from csv")
    with open('reviews2.csv') as cfile:
        creader = csv.reader(cfile,delimiter=',')
        l = 0
        for r in creader:
            if l > 0:
                movie_query = Movie.objects.filter(Q(imdbID=r[9]))
            
                if not movie_query:
                    print("##################################### Addind movie %s" % (r[9]))
                    movie = Movie()
                    movie.imdbID = r[9]
                    movie.title = ""
                    
                    updateIMDbData(movie)
                else:
                    movie = movie_query[0]
                    print("##################################### Updating movie %s" % (r[9]))
                    
                
                #updateIMDbData(movie)
                

                # mv = getIMDbData(movie)

                # if mv != "ERROR":
                #    mv.save()
                
                review_query = Review.objects.filter(Q(author__username=r[8]),Q(movie_id=r[9]))

                if not review_query:
                    review = Review()      

                    review.author_id = r[8]
                    review.movie_id = r[9]
                    review.sv = r[4]
                    review.sf = r[5]
                    review.notes = r[2]
                    review.text = r[1]
                    review.added = r[3]
                    review.special = r[7]

                    review.save()
            l += 1
