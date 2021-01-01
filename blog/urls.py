from django.urls import path
from . import views
from .views import PostIndexView, PostDetailView, VisitorDetailView, VisitorListView

app_name = 'blog'

urlpatterns = [
    path('index/<int:blog_id>/<slug:slug>/', views.PostIndexView.as_view(), name='index'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', PostDetailView.as_view(), name='detail'),
    path('visitor/<int:pk>', VisitorDetailView.as_view(), name='visitor'),
    path('<int:post_id>/share/', views.share, name='share'),
    path('visitor_query/', views.visitor_query, name='visitor-query'),
    path('avatar_select/<str:file>', views.avatar_select, name='avatar-select'),
    path('delete_comment/<int:pk>', views.delete_comment, name='delete_comment'),
    path('move_post_to/<int:post_id>/<int:blog_id>', views.move_post_to, name='move_post_to'),
    path('set_status/<int:post_id>/<str:new_status>', views.set_status, name='set_status'),
    path('visitor_list/', views.VisitorListView.as_view(), name='visitor-list'),
]