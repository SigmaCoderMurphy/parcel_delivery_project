from django.urls import path
from django.contrib.sitemaps.views import sitemap

from . import views
from .sitemaps import PublicStaticSitemap

sitemaps = {'pages': PublicStaticSitemap}

urlpatterns = [
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('access-denied/', views.access_denied, name='access_denied'),
    path('logout/', views.user_logout, name='logout'),
]