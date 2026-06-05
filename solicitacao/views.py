from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from pet.models import Pet
from solicitacao.forms import FormularioAvaliacaoSolicitacao, FormularioSolicitacao
from solicitacao.models import SolicitacaoDeAdocao
from solicitacao.serializers import SerializadorSolicitacaoDeAdocao
from user.consts import TIPO_ADOTANTE, TIPO_ONG
from user.utils import get_custom_user_for_request


class ListarSolicitacoes(LoginRequiredMixin, ListView):
    # view para listar solicitações de adoção
    model = SolicitacaoDeAdocao
    context_object_name = 'solicitacoes'
    template_name = 'solicitacao/listar_solicitacoes.html'

    def get_queryset(self, **kwargs):
        pesquisa = self.request.GET.get('pesquisa')
        custom_user = get_custom_user_for_request(self.request)
        queryset = SolicitacaoDeAdocao.objects.select_related('adotante', 'pet', 'pet__responsavel')

        if pesquisa is not None:
            queryset = queryset.filter(pet__nome__icontains=pesquisa)

        if self.request.user.is_superuser:
            return queryset

        if not custom_user:
            return queryset.none()

        if custom_user.tipo_usuario == TIPO_ONG:
            queryset = queryset.filter(pet__responsavel=custom_user)
        elif custom_user.tipo_usuario == TIPO_ADOTANTE:
            queryset = queryset.filter(adotante=custom_user)

        return queryset


class CriarSolicitacao(LoginRequiredMixin, CreateView):
    # view para criar uma nova solicitação de adoção
    model = SolicitacaoDeAdocao
    form_class = FormularioSolicitacao
    template_name = 'solicitacao/nova_solicitacao.html'

    def dispatch(self, request, *args, **kwargs):
        self.pet = Pet.objects.filter(pk=kwargs.get('pet_pk'), status='1').first()
        self.custom_user = get_custom_user_for_request(request)

        if not self.pet:
            return redirect('home_pets')

        if not self.custom_user or self.custom_user.tipo_usuario != TIPO_ADOTANTE:
            return redirect('detalhe_pet', pk=self.pet.pk)

        solicitacao_existente = SolicitacaoDeAdocao.objects.filter(
            adotante=self.custom_user,
            pet=self.pet,
        ).exists()
        if solicitacao_existente:
            return redirect('listar_solicitacoes')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.adotante = self.custom_user
        form.instance.pet = self.pet
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pet'] = self.pet
        return context

    def get_success_url(self):
        return reverse('listar_solicitacoes')


class EditarSolicitacao(LoginRequiredMixin, UpdateView):
    # view para avaliar uma solicitação existente
    model = SolicitacaoDeAdocao
    form_class = FormularioAvaliacaoSolicitacao
    template_name = 'solicitacao/editar_solicitacao.html'
    success_url = reverse_lazy('listar_solicitacoes')

    def get_queryset(self):
        custom_user = get_custom_user_for_request(self.request)
        queryset = SolicitacaoDeAdocao.objects.select_related('adotante', 'pet', 'pet__responsavel')

        if self.request.user.is_superuser:
            return queryset

        if not custom_user:
            return queryset.none()

        if custom_user.tipo_usuario == TIPO_ONG:
            return queryset.filter(pet__responsavel=custom_user)
        return queryset.none()

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.object.status == 'APROVADA':
            self.object.pet.status = '3'
            self.object.pet.save()
        return response


class DeletarSolicitacao(LoginRequiredMixin, DeleteView):
    # view para deletar uma solicitação existente
    model = SolicitacaoDeAdocao
    template_name = 'solicitacao/deletar_solicitacao.html'
    success_url = reverse_lazy('listar_solicitacoes')

    def get_queryset(self):
        custom_user = get_custom_user_for_request(self.request)
        queryset = SolicitacaoDeAdocao.objects.select_related('adotante', 'pet', 'pet__responsavel')

        if self.request.user.is_superuser:
            return queryset

        if not custom_user:
            return queryset.none()

        if custom_user.tipo_usuario == TIPO_ONG:
            return queryset.filter(pet__responsavel=custom_user)
        return queryset.filter(adotante=custom_user, status='PENDENTE')


class APIListarSolicitacoes(ListAPIView):
    # view para listar instâncias de solicitações por meio de API REST
    serializer_class = SerializadorSolicitacaoDeAdocao
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        custom_user = get_custom_user_for_request(self.request)
        queryset = SolicitacaoDeAdocao.objects.select_related('adotante', 'pet', 'pet__responsavel')

        if self.request.user.is_superuser:
            return queryset

        if not custom_user:
            return queryset.none()

        if custom_user.tipo_usuario == TIPO_ONG:
            return queryset.filter(pet__responsavel=custom_user)
        return queryset.filter(adotante=custom_user)
