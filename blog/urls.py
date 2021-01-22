from django.urls import path
from . import views, blogs
from .views import PostIndexView, PostDetailView, VisitorDetailView, VisitorListView, PostEditView
from .blogs import BlogListView

# Debug logging only
import logging
logger = logging.getLogger(__name__)

app_name = 'blog'

urlpatterns = [
    path('index/<int:blog_id>/<slug:slug>/', views.PostIndexView.as_view(query_status='published'), name='index'),
    path('index/draft/<int:blog_id>/', views.PostIndexView.as_view(query_status='draft'), name='index-draft'),
    path('index/deleted/<int:blog_id>/', views.PostIndexView.as_view(query_status='deleted'), name='index-deleted'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', PostDetailView.as_view(), name='detail'),
    path('visitor/<int:pk>', VisitorDetailView.as_view(), name='visitor'),
    path('<int:post_id>/share/', views.share, name='share'),
    path('visitor_query/', views.visitor_query, name='visitor-query'),
    path('avatar_select/<str:file>', views.avatar_select, name='avatar-select'),
    path('delete_comment/<int:pk>', views.delete_comment, name='delete_comment'),
    path('move_post_to/<int:post_id>/<int:blog_id>', views.move_post_to, name='move_post_to'),
    path('set_status/<int:post_id>/<str:new_status>', views.set_status, name='set_status'),
    path('visitor_list/', views.VisitorListView.as_view(), name='visitor-list'),
    path('edit_post/<int:pk>', PostEditView.as_view(), name='edit-post'),
    path('get_preview/', views.get_preview, name='get-preview'),
    path('like/', views.like_comment, name='like'),
    path('blog_list/', blogs.BlogListView.as_view(), name='blog-list'),
]
