from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
import pdb


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')

class Blog(models.Model):
    STATUS_CHOICES = (
        ('dormant', 'Dormant'),
        ('offline', 'Offline'),
        ('online', 'Online'),
    )

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                            on_delete=models.CASCADE,
                            related_name='blogs')
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='offline')
    banner = models.ImageField(
                upload_to='images/banners/',
                blank=True,
                default='',
                storage=FileSystemStorage(
                            location=settings.MEDIA_BANNER_FILES,
                            base_url=settings.MEDIA_BANNER_URL))
    description = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    last_post = models.DateTimeField(null=True)

    def update_last_post(self):
        self.last_post = timezone.now()
        self.save()


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250,
                            unique_for_date='publish')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='blog_posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
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
    name = models.CharField(max_length=28, unique=True)
    pin = models.CharField(max_length=6)
    last_visit = models.DateTimeField(auto_now=True)
    avatar = models.ImageField(
                upload_to='images/avatars/',
                storage=FileSystemStorage(
                            location=settings.MEDIA_AVATAR_FILES,
                            base_url=settings.MEDIA_AVATAR_URL),
                default="SeekPng.com_avatar-png_1150362.png")

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

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return f"[{self.visitor}]@{self.created}"