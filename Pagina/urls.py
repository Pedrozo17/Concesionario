from django.urls import path
from . import views

urlpatterns = [

    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard),

    path('carros/crear/', views.crear_carro, name='crear_carro'),
    path('carros/<str:carro_id>/', views.ver_carro, name='ver_carro'),
    path('carros/editar/<str:carro_id>/', views.editar_carro, name='editar_carro'),
    path('carros/eliminar/<str:carro_id>/', views.eliminar_carro, name='eliminar_carro'),
]
