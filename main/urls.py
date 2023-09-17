from django.contrib import admin
from django.urls import path, include
from contact.views import contact_page

from main import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('shop/', include('shop.urls')),
    path('contact/', contact_page, name='contact'),
]
