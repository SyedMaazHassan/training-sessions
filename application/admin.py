from pyexpat import model
from django.contrib import admin
from .models import *
from django.contrib.sessions.models import Session

# Register your models here.
class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1

class MediaInline(admin.StackedInline):
    model = Media
    extra = 1

class TrainingAdmin(admin.ModelAdmin):
    inlines = [ModuleInline]

class ModuleAdmin(admin.ModelAdmin):
    inlines = [MediaInline]

class AccessAdmin(admin.ModelAdmin):
    list_display = ('training', 'user', 'created_at')
    
    # @display(ordering='training__name', description='Training')
    def training(self, obj):
        return obj.training.name

    def user(self, obj):
        return obj.user.first_name

admin.site.register(Term)
admin.site.register(Bookmark)
admin.site.register(Learning)
admin.site.register(Folder)
admin.site.register(Session)
admin.site.register(Training, TrainingAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Media)
admin.site.register(Access, AccessAdmin)