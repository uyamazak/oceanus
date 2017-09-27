from django.contrib import admin
from .models import Query, QueryAdmin


admin.site.register(Query, QueryAdmin)
