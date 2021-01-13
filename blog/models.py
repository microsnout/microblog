from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from model_utils import Choices
import os
import pdb
from urllib.parse import urljoin

@deconstructible
class MyFileSystemStorage(FileSystemStorage):
    def __init__(self, subdir):
        self.subdir = subdir
        super(MyFileSystemStorage, self).__init__(
                location=os.path.join(settings.MEDIA_ROOT, self.subdir), 
                base_url=urljoin(settings.MEDIA_URL, self.subdir))

    def __eq__(self, other):
        return self.subdir == other.subdir

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')

class Blog(models.Model):
    STATUS = Choices( 'dormant', 'offline', 'online' )
    status_values = [v[0] for v in STATUS]

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                            on_delete=models.CASCADE,
                            related_name='blogs')
    status = models.CharField(max_length=10,
                              choices=STATUS,
                              default='offline')
    banner = models.ImageField(
                upload_to= 'images/banners/',
                blank= True,
                default= '',
                storage= MyFileSystemStorage('images/banners/'))
    description = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    last_post = models.DateTimeField(null=True)
    one_comment = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:index',
                       args=[self.id, self.slug])

    def update_last_post(self):
        self.last_post = timezone.now()
        self.save()


class Post(models.Model):
    STATUS = Choices( 'draft', 'published', 'deleted' )
    status_values = [v[0] for v in STATUS]

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250,
                            unique_for_date='publish')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='blog_posts')
    blog = models.ForeignKey( Blog,
                              on_delete=models.CASCADE,
                              related_name='posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,
                              choices=STATUS,
                              default='draft')

    objects = models.Manager() # The default manager.
    published = PublishedManager() # Our custom manager.

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day, self.slug])

class Visitor(models.Model):
    DEF_AVATAR = "SeekPng.com_avatar-png_1150362.png"
    DEF_AVATAR_URL = settings.MEDIA_AVATAR_URL + DEF_AVATAR

    name = models.CharField(max_length=28, unique=True)
    pin = models.CharField(max_length=6)
    last_visit = models.DateTimeField(auto_now=True)
    avatar = models.ImageField(
                upload_to= 'images/avatars/',
                storage= MyFileSystemStorage('images/avatars/'),
                default= DEF_AVATAR)

    class Meta:
        ordering = ('-last_visit',)

    def __str__(self):
        return self.name + ':' + self.pin

    def get_absolute_url(self):
        return reverse('blog:visitor',
                       args=[self.pk,])

class Comment (models.Model):
    post = models.ForeignKey(
                    Post,
                    on_delete=models.CASCADE,
                    related_name='comments')
    visitor = models.ForeignKey(
                    Visitor,
                    on_delete=models.CASCADE,
                    related_name='comments')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True) 
    body = models.CharField(max_length=300)
    fans = models.ManyToManyField(
                    Visitor,
                    related_name='comments_liked',
                    blank=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return f"[{self.visitor}]@{self.created}"