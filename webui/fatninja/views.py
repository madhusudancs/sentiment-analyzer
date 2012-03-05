#!/usr/bin/env python
#
# Copyright 2012 Ajay Narayan, Madhusudan C.S., Shobhit N.S.
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The views module for the webui of sentiment analyzer.
"""


import urllib
import datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template import loader

from fatninja.models import MetaData


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

