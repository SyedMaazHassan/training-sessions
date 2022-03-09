from django.contrib import admin
from .models import *
from django.contrib.sessions.models import Session

# Register your models here.
admin.site.register(Term)
admin.site.register(Bookmark)
admin.site.register(Learning)
admin.site.register(Folder)
admin.site.register(Session)
admin.site.register(Device)