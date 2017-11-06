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
from django.contrib.auth import views as auth_views

from shortener.views import index, make, make_article, redirect_original, shorten_url
from lead.views import list_queries, detail_query, download_query, list_custom_queries, detail_custom_query

urlpatterns = [
    url(r'^$', index, name='home'),

    url(r'^oceanusadmin/', include(admin.site.urls), name="admin"),

    url(r'^oceanuslogin/?$', auth_views.login, name='login'),
    url(r'^oceanuslogout/?$', auth_views.logout, {'next_page': '/oceanuslogin/'}, name='logout'),

    url(r'^shortener/make/?$', make, name='make'),
    url(r'^shortener/make_article/?$', make_article, name='make_article'),
    url(r'^shortener/makeshort/?$', shorten_url, name='shortenurl'),

    url(r'^lead/?$', list_queries, name='list_leads'),
    url(r'^lead-custom/?$', list_custom_queries, name='list_custom_leads'),
    url(r'^lead/(?P<query_id>\d+)/?$', detail_query, name='detail_lead'),
    url(r'^lead-custom/(?P<query_id>\d+)/?$', detail_custom_query, name='detail_custom_lead'),
    url(r'^lead/(?P<query_id>\d+)/download/?$', download_query, name='download_lead'),

    url(r'^(?P<short_id>\w{3,16})$', redirect_original, name='redirectoriginal'),
]
if not os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine'):
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)), ]
