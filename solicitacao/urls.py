from django.urls import path

from solicitacao.views import *

urlpatterns = [
    path('', ListarSolicitacoes.as_view(), name='listar_solicitacoes'),
    path('novo/<int:pet_pk>/', CriarSolicitacao.as_view(), name='criar_solicitacao'),
    path('editar/<int:pk>/', EditarSolicitacao.as_view(), name='editar_solicitacao'),
    path('deletar/<int:pk>/', DeletarSolicitacao.as_view(), name='deletar_solicitacao'),
    path('api/listar/', APIListarSolicitacoes.as_view(), name='api_listar_solicitacoes'),
    path('api/novo/<int:pet_pk>/', APICriarSolicitacao.as_view(), name='api_criar_solicitacao'),
    path('api/editar/<int:pk>/', APIEditarSolicitacao.as_view(), name='api_editar_solicitacao'),
]
