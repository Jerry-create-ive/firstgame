from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('test/', views.test_images, name='test_images'),
    path('simple/', views.simple_test, name='simple_test'),
]
