# <app>/templatetags/my_tags.py
from django import template
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag(takes_context=True)
def get_query(context, **kwargs):
    d = context['request'].GET.copy()
    if 'q' in d:
        return d['q']
    else:
        return ""



@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()

@register.simple_tag(takes_context=True)
def param_add(context, **kwargs):
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        if isinstance(v,int):
            d[k] = v
        else:
            if k in d:
                if not v in d[k]:
                    v += ",%s" % (d.copy()[k])
            d[k] = v
    
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    
    return d.urlencode()



@register.simple_tag
def people_split(people):
    r = ""
    for i in range(6):
        pp = people.split(', ')
        if len(pp) > i:
            if len(r) > 0: r += ', '
            #r += pp[i]
            r += '<a href="/?act=%s">%s</a>' % (pp[i],pp[i])

    return mark_safe(r)

@register.simple_tag
def genre_split(genre):
    r = ""
    for i in range(6):
        pp = genre.split(', ')
        if len(pp) > i:
            if len(r) > 0: r += ', '
            #r += pp[i]
            r += '<a style="color:gray" href="/?g=%s">%s</a>' % (pp[i],pp[i])

    return mark_safe(r)


@register.simple_tag(takes_context=True)
def buttons_filter(context):
    d = context['request'].GET.copy()
    clean = d.copy()

    r = ''

    for k,v in d.items():
        if k != 'page':
            if k == 'g' and "," in v:
                for g in v.split(","):
                    nd = d.copy()
                    print("before:",nd[k])
                    nd[k] = nd[k].replace(","+g,"")
                    nd[k] = nd[k].replace(g+",","")
                    print("after:",nd[k])
                    
                    r += '<li><a class="border rounded p-1" href="?%s">x %s</a></li>' % (nd.urlencode(),g)
            else:
                nd = d.copy()
                del nd[k]
                r += '<li><a class="border rounded p-1" href="?%s">x %s</a></li>' % (nd.urlencode(),v)

    
    if r != '':
        r += '<li><a class ="border rounded p-1 text-dark" href="?%s">%s</a></li>' % (clean.urlencode(),'Remove filters')
        r = '%s %s %s' % ('<ul class="pagination justify-content-center">',r,'</ul>')
    
    return mark_safe(r)


@register.simple_tag
def getEditingIcon(icon_id):
    icon = ""
    if icon_id == -1:
        icon = "<i class='fa fa-question text-warning'></i>"
    elif icon_id == 0:
        icon = "<i class='fa fa-times text-danger'></i>"
    elif icon_id == 1:
        icon = "<i class='fa fa-scissors'></i>"
    elif icon_id == 2:
        icon = "<i class='fa fa-check text-success'></i>"
    
    return mark_safe(icon)

@register.simple_tag
def getPosterPath(movie):
    if 'http' in movie.poster_path:
        pp = movie.poster_path
    else:
        if movie.backdrop_path == '':
            pp = "https://image.tmdb.org/t/p/w342" + movie.poster_path
        else:
            pp = "https://image.tmdb.org/t/p/w154" + movie.poster_path
    
    return pp

@register.simple_tag
def get_certification(cert):
    r = ""
    cs = cert.split(',')
    for c in cs:
        if r: r += ", "
        fc = c.split(":")
        r += "%s: <span class='certification'>%s</span>" % (fc[0],fc[1])
    
    return mark_safe(r)


