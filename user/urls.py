from django.urls import path

from user.views import *

urlpatterns = [
    path('', ListarUsuarios.as_view(), name='listar_usuarios'),
    path('cadastro/', CadastroUsuario.as_view(), name='cadastro_usuario'),
    path('novo/', CriarUsuario.as_view(), name='criar_usuario'),
    path('editar/<int:pk>/', EditarUsuario.as_view(), name='editar_usuario'),
    path('deletar/<int:pk>/', DeletarUsuario.as_view(), name='deletar_usuario'),
    path('api/listar/', APIListarUsuarios.as_view(), name='api_listar_usuarios'),
]
