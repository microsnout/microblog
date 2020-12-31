from django.urls import path
from . import views
from .views import PostIndexView, PostDetailView, VisitorDetailView

app_name = 'blog'

urlpatterns = [
    path('index/<int:blog_id>/<slug:slug>/', views.PostIndexView.as_view(), name='index'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/',
        PostDetailView.as_view(),
        name='detail'),
    path('<int:pk>/visitor/', VisitorDetailView.as_view(), name='visitor'),
    path('<int:post_id>/share/', views.share, name='share'),
    path('visitor_query/', views.visitor_query, name='visitor-query'),
    path('avatar_select/<str:file>', views.avatar_select, name='avatar-select'),
    path('delete_comment/<int:pk>', views.delete_comment, name='delete_comment'),
]