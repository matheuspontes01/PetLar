from django.urls import path

from pet.views import *

urlpatterns = [
    path('adocao/', HomePets.as_view(), name='home_pets'),
    path('adocao/<int:pk>/', DetalhePet.as_view(), name='detalhe_pet'),
    path('', ListarPets.as_view(), name='listar_pets'),
    path('novo/', CriarPet.as_view(), name='criar_pet'),
    path('editar/<int:pk>/', EditarPet.as_view(), name='editar_pet'),
    path('deletar/<int:pk>/', DeletarPet.as_view(), name='deletar_pet'),
    path('api/listar/', APIListarPets.as_view(), name='api_listar_pets'),
]
