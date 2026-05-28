from django.urls import path
from main import views

urlpatterns = [
    path('', views.index, name='index'),
    # API接口
    path('api/calculate-spirit/', views.calculate_spirit, name='calculate_spirit'),
    path('api/determine-ending/', views.determine_ending, name='determine_ending'),
    path('api/game-config/', views.get_game_config, name='get_game_config'),
]
