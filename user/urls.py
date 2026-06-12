from django.urls import path

from user.views import *

urlpatterns = [
    path('', ListarUsuarios.as_view(), name='listar_usuarios'),
    path('ongs-pendentes/', ListarOngsPendentes.as_view(), name='listar_ongs_pendentes'),
    path('cadastro/', CadastroUsuario.as_view(), name='cadastro_usuario'),
    path('novo/', CriarUsuario.as_view(), name='criar_usuario'),
    path('editar/<int:pk>/', EditarUsuario.as_view(), name='editar_usuario'),
    path('deletar/<int:pk>/', DeletarUsuario.as_view(), name='deletar_usuario'),
    path('api/listar/', APIListarUsuarios.as_view(), name='api_listar_usuarios'),
    path('api/gerenciar/', APIGerenciarUsuarios.as_view(), name='api_gerenciar_usuarios'),
    path('api/gerenciar/<int:pk>/', APIEditarUsuario.as_view(), name='api_editar_usuario'),
]
