from django.contrib import admin
from .models import Post, Comment, Visitor

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('visitor', 'body')

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'pin', 'last_visit')
    list_filter = ('name', 'pin', 'last_visit')
    search_fields = ('name',)
    