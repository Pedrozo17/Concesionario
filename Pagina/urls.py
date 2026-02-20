from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard),

    path('carros/crear/', views.crear_carro, name='crear_carro'),
    path('carros/<str:carro_id>/', views.ver_carro, name='ver_carro'),
    path('carros/<str:carro_id>/editar/', views.editar_carro, name='editar_carro'),
    path('carros/<str:carro_id>/eliminar/', views.eliminar_carro, name='eliminar_carro'),

    # 🔥 ESTA ES LA QUE TE FALTA
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),

    path('login/', views.iniciar_sesion, name='login'),
    path('registro/', views.registro_usuario, name='registro'),
]