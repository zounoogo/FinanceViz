# visualization/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),  # Page d'accueil
    path('visualize_tab/', views.visualize_TabData, name='visualize_tab'),
    path('visualize_csv/', views.visualize_CSVData, name='visualize_csv'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
]
