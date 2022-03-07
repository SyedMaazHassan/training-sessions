from django.db import models
from datetime import datetime
from django.contrib.auth.models import User, auth
from django.utils import timezone
import html2text

# Create your models here.

# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver



class Category(models.Model):
    name = models.CharField(max_length = 100)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    created_at = models.DateTimeField(default = timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-id",)



class Topic(models.Model):
    name = models.CharField(max_length = 100)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    created_at = models.DateTimeField(default = timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-id",)

    
class Folder(models.Model):
    name = models.CharField(max_length = 100)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    is_delete_allowed = models.BooleanField(default = False)
    created_at = models.DateTimeField(default = timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-id",)

class Term(models.Model):
    title = models.CharField(max_length = 100)
    category = models.ForeignKey(Category, on_delete = models.SET_NULL, null = True)
    topics = models.ManyToManyField(Topic)
    typee = models.CharField(max_length = 10, choices = [('Word', 'Word'), ('Phrase', 'Phrase'), ('Term', 'Term')])
    content = models.TextField()
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank = True)
    folder = models.ForeignKey(Folder, on_delete = models.CASCADE, null = True, blank = True)
    created_at = models.DateTimeField(default = timezone.now)

    def get_short_text_only(self):
        return self.terminate(self.get_text_only(), 526)

    def get_text_only(self):
        text = html2text.html2text(self.content)
        return text

    def terminate(self, string, limit = 30):
        if len(string) >= limit:
            return string[0: limit] + "..."
        return string

    def actual_title(self):
        my_title = self.title.capitalize() 
        return self.terminate(my_title)

    def serialize_object(self):
        return {
            "title": self.actual_title(),
            "content": self.content,
            "category": self.category.name if self.category else None,
            "topics": list(self.topics.all().values_list("name"))
        }

    def save(self, *args, **kwargs):
        # figure out warranty end date
        self.title = self.title.lower()
        super(Term, self).save(*args, **kwargs)   

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("-id",)


class Bookmark(models.Model):
    CHOICES = [
        ('yellow', 'Yellow'),
        ('green', 'Green'),
        ('blue', 'Blue'),
        ('purple', 'Purple'),
        ('red', 'Red'),
    ]
    title = models.CharField(max_length = 255)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    source = models.ForeignKey(Term, on_delete = models.SET_NULL, null = True)
    color = models.CharField(max_length = 50, choices = CHOICES, default='yellow')
    comment = models.TextField(null = True, blank = True)
    created_at = models.DateTimeField(default = timezone.now)

    def get_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'color': self.color,
            'comment': self.comment
        }

    class Meta:
        ordering = ("-id",)


class Learning(models.Model):
    query = models.CharField(max_length = 255)
    term = models.ForeignKey(Term, on_delete = models.CASCADE, null = True, blank = True)
    bookmark = models.ForeignKey(Bookmark, on_delete = models.CASCADE, null = True, blank = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    created_at = models.DateTimeField(default = timezone.now)

    def clip_text(self, limit = 30):
        if len(self.query) >= limit:
            return self.query[0: limit] + "..."
        return self.query

    class Meta:
        ordering = ("id",)


