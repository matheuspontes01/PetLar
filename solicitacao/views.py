from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from PetLar.mixins import PerfilUsuarioMixin, get_custom_user_for_request
from pet.models import Pet
from solicitacao.forms import FormularioAvaliacaoSolicitacao, FormularioSolicitacao
from solicitacao.models import SolicitacaoDeAdocao
from solicitacao.serializers import SerializadorSolicitacaoDeAdocao
from user.consts import TIPO_ADOTANTE, TIPO_ONG


class ListarSolicitacoes(PerfilUsuarioMixin, LoginRequiredMixin, ListView):
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


class CriarSolicitacao(PerfilUsuarioMixin, LoginRequiredMixin, CreateView):
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


class EditarSolicitacao(PerfilUsuarioMixin, LoginRequiredMixin, UpdateView):
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


class DeletarSolicitacao(PerfilUsuarioMixin, LoginRequiredMixin, DeleteView):
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


class APICriarSolicitacao(APIView):
    # view para criar solicitações de adoção por meio de API REST
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pet_pk):
        custom_user = get_custom_user_for_request(request)
        pet = Pet.objects.filter(pk=pet_pk, status='1').first()

        if not pet:
            return Response({'detail': 'Pet não disponível para adoção.'}, status=400)

        if not custom_user or custom_user.tipo_usuario != TIPO_ADOTANTE:
            return Response({'detail': 'Somente adotantes podem solicitar adoção.'}, status=403)

        if SolicitacaoDeAdocao.objects.filter(adotante=custom_user, pet=pet).exists():
            return Response({'detail': 'Você já possui uma solicitação para este pet.'}, status=400)

        solicitacao = SolicitacaoDeAdocao.objects.create(
            adotante=custom_user,
            pet=pet,
            mensagem=request.data.get('mensagem') or 'Tenho interesse na adoção.',
        )
        serializer = SerializadorSolicitacaoDeAdocao(solicitacao)
        return Response(serializer.data, status=201)


class APIEditarSolicitacao(APIView):
    # view para avaliar ou cancelar solicitações por meio de API REST
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        custom_user = get_custom_user_for_request(request)
        solicitacao = self.get_solicitacao(request, custom_user, pk, permitir_adotante=False)

        if not solicitacao:
            return Response({'detail': 'Solicitação não encontrada.'}, status=404)

        status_solicitacao = request.data.get('status')
        if status_solicitacao not in ['PENDENTE', 'APROVADA', 'REJEITADA']:
            return Response({'detail': 'Status inválido.'}, status=400)

        solicitacao.status = status_solicitacao
        solicitacao.save()

        if solicitacao.status == 'APROVADA':
            solicitacao.pet.status = '3'
            solicitacao.pet.save()

        serializer = SerializadorSolicitacaoDeAdocao(solicitacao)
        return Response(serializer.data)

    def delete(self, request, pk):
        custom_user = get_custom_user_for_request(request)
        solicitacao = self.get_solicitacao(request, custom_user, pk, permitir_adotante=True)

        if not solicitacao:
            return Response({'detail': 'Solicitação não encontrada.'}, status=404)

        solicitacao.delete()
        return Response(status=204)

    def get_solicitacao(self, request, custom_user, pk, permitir_adotante):
        queryset = SolicitacaoDeAdocao.objects.select_related('adotante', 'pet', 'pet__responsavel')

        if request.user.is_superuser:
            return queryset.filter(pk=pk).first()

        if not custom_user:
            return None

        if custom_user.tipo_usuario == TIPO_ONG:
            return queryset.filter(pk=pk, pet__responsavel=custom_user).first()

        if permitir_adotante and custom_user.tipo_usuario == TIPO_ADOTANTE:
            return queryset.filter(pk=pk, adotante=custom_user, status='PENDENTE').first()

        return None
