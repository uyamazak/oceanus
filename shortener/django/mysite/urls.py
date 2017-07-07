# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from django.conf.urls import include, url
from django.contrib import admin
from shortener.views import index, make, make_article, redirect_original, shorten_url

urlpatterns = [
    url(r'^oceanusadmin/', include(admin.site.urls), name="admin"),
    url(r'^$', index, name='home'),
    url(r'^make/$', make, name='make'),
    url(r'^make_article/$', make_article, name='make_article'),
    url(r'^makeshort/$', shorten_url, name='shortenurl'),
    url(r'^(?P<short_id>\w{3,12})$', redirect_original, name='redirectoriginal'),
]
if not os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine'):
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)), ]
