from django.urls import path
from . import views
urlpatterns = [
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('carros/crear/', views.crear_carro, name='crear_carro'),
    path('carros/<str:carro_id>/', views.ver_carro, name='ver_carro'),
    path('carros/editar/<str:carro_id>/', views.editar_carro, name='editar_carro'),
    path('carros/eliminar/<str:carro_id>/', views.eliminar_carro, name='eliminar_carro'),
]
