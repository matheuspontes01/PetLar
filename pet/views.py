from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View
from django.http import FileResponse, Http404

from pet.forms import FormularioPet
from pet.models import Pet
from PetLar.mixins import PetManagerRequiredMixin
from user.models import User

# Create your views here.
class HomePets(LoginRequiredMixin, ListView):
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
    model = Pet
    template_name = 'pet/listar_pets.html'
    context_object_name = 'pets'

    def get_queryset(self, **kwargs):
        pesquisa = self.request.GET.get('pesquisa')
        queryset = Pet.objects.select_related('responsavel').all()
        if self.custom_user.tipo_usuario == User.TipoUsuario.ONG:
            queryset = queryset.filter(responsavel=self.custom_user)
        if pesquisa is not None:
            queryset = queryset.filter(nome__icontains=pesquisa)
        return queryset


class DetalhePet(LoginRequiredMixin, DetailView):
    model = Pet
    template_name = 'pet/detalhe_pet.html'
    context_object_name = 'pet'
    
class CriarPet(PetManagerRequiredMixin, CreateView):
    model = Pet
    form_class = FormularioPet
    template_name = 'pet/novo_pet.html'
    success_url = reverse_lazy('listar_pets')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.custom_user
        return kwargs

    def form_valid(self, form):
        if self.custom_user.tipo_usuario == User.TipoUsuario.ONG:
            form.instance.responsavel = self.custom_user
        return super().form_valid(form)


class EditarPet(PetManagerRequiredMixin, UpdateView):
    model = Pet
    form_class = FormularioPet
    template_name = 'pet/editar_pet.html'
    success_url = reverse_lazy('listar_pets')

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.custom_user.tipo_usuario == User.TipoUsuario.ONG:
            queryset = queryset.filter(responsavel=self.custom_user)
        return queryset

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.custom_user
        return kwargs

    def form_valid(self, form):
        if self.custom_user.tipo_usuario == User.TipoUsuario.ONG:
            form.instance.responsavel = self.custom_user
        return super().form_valid(form)


class DeletarPet(PetManagerRequiredMixin, DeleteView):
    model = Pet
    template_name = 'pet/deletar_pet.html'
    success_url = reverse_lazy('listar_pets')

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.custom_user.tipo_usuario == User.TipoUsuario.ONG:
            queryset = queryset.filter(responsavel=self.custom_user)
        return queryset

class FotosPet(View):
    def get(self, request, arquivo):
        try:
            pet = Pet.objects.get(fotos='pets/{}'.format(arquivo))
            return FileResponse(pet.fotos)
        except Pet.DoesNotExist:
            raise Http404("Foto não encontrada ou acesso não autorizado.")
        except Exception as e:
            raise e
