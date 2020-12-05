from django.urls import path
from . import views
from .views import PostIndexView

app_name = 'blog'

urlpatterns = [
    path('', views.PostIndexView.as_view(), name='index'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',
        views.detail,
        name='detail'),
]