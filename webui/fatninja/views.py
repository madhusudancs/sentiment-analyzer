import urllib
import datetime

from django.template  import RequestContext, loader
from django.http      import HttpResponse
from fatninja.models  import MetaData
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

def index(request):
#    query_list = MetaData.objects.all()
#    t = loader.get_template('fatninja/hero.html')
#    c = Context({'query_list':query_list, })
#    return HttpResponse(t.render(c))
    if request.method == 'POST':
        post_data = request.POST
        
        query = post_data.get('query', None)
        if query:
            meta_object = MetaData.objects.create(search_key = query, search_stamp=datetime.datetime.now())
            meta_object.save()
            return redirect('%s?%s' % (reverse('fatninja.views.index'), urllib.urlencode({'q': query})))
    elif request.method == 'GET':
        

    return render_to_response('fatninja/hero.html', RequestContext(request, {}))

