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


# Custom Model for the Device 
class Device(models.Model):
    browser = models.CharField(max_length=50)
    device = models.CharField(max_length=50)
    device_type = models.CharField(max_length=50)
    os = models.CharField(max_length=20)
    ip = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)


    # method to fetch the ip of client 
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    # Function for checking the browser, IP-address, and device info of the user
    def set_browser_info(self, request):

        # status of mobile, pc or tablet
        is_mobile = request.user_agent.is_mobile
        is_tablet = request.user_agent.is_tablet 
        is_pc = request.user_agent.is_pc

        if is_mobile:
            self.device_type = 'mobile'
        elif is_tablet:
            self.device_type = 'tablet'
        elif is_pc:
            self.device_type = 'pc or laptop' 
        else:
            self.device_type = 'unknown'
                
        # fetching the browser info
        browser_family = request.user_agent.browser.family
        self.browser = browser_family
        browser_version = request.user_agent.browser.version

        # fetching the os info
        os_family = request.user_agent.os.family
        self.os = os_family
        os_version = request.user_agent.os.version

        # fetching the device info
        device_name = request.user_agent.device.family
        self.device = device_name

        ip = self.get_client_ip(request)
        self.ip = ip
    
    def is_already_exists(self):
        devices = Device.objects.filter(
            user=self.user,
            browser=self.browser,
            device = self.device,
            device_type = self.device_type,
            os = self.os,
            ip = self.ip)

        return devices.exists()

    def is_limit_reached(self, limit=4):
        devices = Device.objects.filter(user=self.user)
        return not devices.count() < limit







