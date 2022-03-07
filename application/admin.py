from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Term)
admin.site.register(Bookmark)
admin.site.register(Learning)
admin.site.register(Folder)