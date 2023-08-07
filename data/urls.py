from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('laptimes/', views.laptimes_distribution, name='laptimes_distribution'),
    path('get-races/', views.get_races, name='get_races'),
    path('get-drivers/', views.get_drivers, name="get_drivers"),
    path('speedtrace/', views.speed_trace, name='speed_trace'),
    path('qualifyingresults', views.qualifying_results, name="qualifying_results"),
    path('livetiming/', views.live_timing, name='live_timing'),
    path('positionchanges/', views.position_changes, name='position_changes'),
    path('error/', views.error_page, name='error_page')
]
