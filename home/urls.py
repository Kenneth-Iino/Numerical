from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('fit/', views.fit, name='fit'),
    path('predictData/', views.predictData, name='predictData'),
    path('regression/', views.regression, name='regression'),
]