from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ipo_app import views

router = DefaultRouter()
router.register(r'ipos', views.IPOViewSet, basename='ipo')
router.register(r'historical', views.HistoricalIPOViewSet, basename='historical')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('ipo/upcomming', views.ipo_upcomming, name='ipo_upcomming'),
    path('ipo/past', views.ipo_past, name='ipo_past'),
    path('ipo/<int:company_id>/', views.ipo_detail, name='ipo_detail'),
    path('api/', include(router.urls)),
    path('api/predict/', views.predict_api, name='predict_api'),
]