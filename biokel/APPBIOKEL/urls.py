from django.urls import path
from .views import login_view, logout_view, inicio, raciones, huevos, reportes, inventario, registrarse

urlpatterns = [
    path('', inicio, name='inicio'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('raciones/', raciones, name='raciones'),
    path('huevos/', huevos, name='huevos'),
    path('metricas/', reportes, name='metricas'),
    path('inventario/', inventario, name='inventario'),
    path("registrarse/", registrarse, name="registrarse"),



]
