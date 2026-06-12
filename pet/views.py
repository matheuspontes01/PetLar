from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import FileResponse, Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from pet.forms import FormularioPet
from pet.models import Pet
from pet.serializers import SerializadorGerenciarPet, SerializadorPet
from PetLar.mixins import PerfilUsuarioMixin, PetManagerRequiredMixin, get_custom_user_for_request
from user.consts import TIPO_ONG

# Create your views here.
class HomePets(PerfilUsuarioMixin, LoginRequiredMixin, ListView):
    # view para listar pets disponíveis para adoção
    model = Pet
    template_name = 'pet/home_pets.html'
    context_object_name = 'pets'

    def get_queryset(self, **kwargs):
        pesquisa = self.request.GET.get('pesquisa')
        queryset = Pet.objects.filter(status='1').select_related('responsavel').order_by('-data_cadastro')
        if pesquisa:
            queryset = queryset.filter(nome__icontains=pesquisa)
        return queryset


class ListarPets(PetManagerRequiredMixin, ListView):
    # view para listar pets cadastrados
    model = Pet
    template_name = 'pet/listar_pets.html'
    context_object_name = 'pets'

    def get_queryset(self, **kwargs):
        pesquisa = self.request.GET.get('pesquisa')
        queryset = Pet.objects.select_related('responsavel').all()
        if self.custom_user and self.custom_user.tipo_usuario == TIPO_ONG:
            queryset = queryset.filter(responsavel=self.custom_user)
        if pesquisa is not None:
            queryset = queryset.filter(nome__icontains=pesquisa)
        return queryset


class DetalhePet(PerfilUsuarioMixin, LoginRequiredMixin, DetailView):
    # view para exibir os detalhes do pet
    model = Pet
    template_name = 'pet/detalhe_pet.html'
    context_object_name = 'pet'

    def get_queryset(self):
        queryset = Pet.objects.select_related('responsavel')

        if self.request.user.is_superuser:
            return queryset

        custom_user = get_custom_user_for_request(self.request)
        filtros = Q(status='1')

        if custom_user and custom_user.tipo_usuario == TIPO_ONG:
            filtros = filtros | Q(responsavel=custom_user)

        return queryset.filter(filtros)
    
class CriarPet(PetManagerRequiredMixin, CreateView):
    # view para criar um novo pet
    model = Pet
    form_class = FormularioPet
    template_name = 'pet/novo_pet.html'
    success_url = reverse_lazy('listar_pets')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.custom_user
        return kwargs

    def form_valid(self, form):
        if self.custom_user and self.custom_user.tipo_usuario == TIPO_ONG:
            form.instance.responsavel = self.custom_user
        return super().form_valid(form)


class EditarPet(PetManagerRequiredMixin, UpdateView):
    # view para editar um pet existente
    model = Pet
    form_class = FormularioPet
    template_name = 'pet/editar_pet.html'
    success_url = reverse_lazy('listar_pets')

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.custom_user and self.custom_user.tipo_usuario == TIPO_ONG:
            queryset = queryset.filter(responsavel=self.custom_user)
        return queryset

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.custom_user
        return kwargs

    def form_valid(self, form):
        if self.custom_user and self.custom_user.tipo_usuario == TIPO_ONG:
            form.instance.responsavel = self.custom_user
        return super().form_valid(form)


class DeletarPet(PetManagerRequiredMixin, DeleteView):
    # view para deletar um pet existente
    model = Pet
    template_name = 'pet/deletar_pet.html'
    success_url = reverse_lazy('listar_pets')

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.custom_user and self.custom_user.tipo_usuario == TIPO_ONG:
            queryset = queryset.filter(responsavel=self.custom_user)
        return queryset

class FotosPet(View):
    # view para exibir a foto do pet
    def get(self, request, arquivo):
        try:
            pet = Pet.objects.get(fotos='pets/{}'.format(arquivo))
            return FileResponse(pet.fotos)
        except ObjectDoesNotExist:
            raise Http404("Foto não encontrada ou acesso não autorizado.")
        except Exception as exception:
            raise exception


class APIListarPets(ListAPIView):
    # view para listar instâncias de pets por meio de API REST
    serializer_class = SerializadorPet
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pesquisa = self.request.GET.get('pesquisa')
        queryset = Pet.objects.filter(status='1').select_related('responsavel').order_by('-data_cadastro')
        if pesquisa is not None:
            queryset = queryset.filter(nome__icontains=pesquisa)
        return queryset


class APIGerenciarPets(ListCreateAPIView):
    # view para listar e criar pets por meio de API REST
    serializer_class = SerializadorGerenciarPet
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pesquisa = self.request.GET.get('pesquisa')
        custom_user = get_custom_user_for_request(self.request)
        queryset = Pet.objects.select_related('responsavel').order_by('-data_cadastro')

        if self.request.user.is_superuser:
            pass
        elif custom_user and custom_user.tipo_usuario == TIPO_ONG and custom_user.ong_aprovada:
            queryset = queryset.filter(responsavel=custom_user)
        else:
            return queryset.none()

        if pesquisa is not None:
            queryset = queryset.filter(nome__icontains=pesquisa)
        return queryset

    def perform_create(self, serializer):
        custom_user = get_custom_user_for_request(self.request)
        if custom_user and custom_user.tipo_usuario == TIPO_ONG:
            serializer.save(responsavel=custom_user)
        else:
            serializer.save()


class APIEditarPet(RetrieveUpdateDestroyAPIView):
    # view para editar e deletar pets por meio de API REST
    serializer_class = SerializadorGerenciarPet
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        custom_user = get_custom_user_for_request(self.request)
        queryset = Pet.objects.select_related('responsavel')

        if self.request.user.is_superuser:
            return queryset

        if custom_user and custom_user.tipo_usuario == TIPO_ONG and custom_user.ong_aprovada:
            return queryset.filter(responsavel=custom_user)

        return queryset.none()

    def perform_update(self, serializer):
        custom_user = get_custom_user_for_request(self.request)
        if custom_user and custom_user.tipo_usuario == TIPO_ONG:
            serializer.save(responsavel=custom_user)
        else:
            serializer.save()
