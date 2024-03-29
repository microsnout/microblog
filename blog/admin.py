from django.contrib import admin
from .models import Blog, Post, Comment, Visitor

# Debug logging only
import logging
logger = logging.getLogger(__name__)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'owner', 'status', 'banner', 'description')
    list_filter = ('status', 'owner')
    search_fields = ('title', 'description')
    prepopulated_fields = { 'slug': ('title',)}
    date_hierarchy = 'last_post'
    ordering = ('owner', 'status', 'title')
    exclude = ('last_post',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'blog', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author', 'blog')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'post', 'created', 'approved')
    list_filter = ('created', 'updated')
    search_fields = ('visitor', 'body')

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'pin', 'last_visit')
    list_filter = ('name', 'pin', 'last_visit')
    search_fields = ('name',)
