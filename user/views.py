from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.contrib.auth import login
from django.contrib.auth.models import User as AuthUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from user.consts import *
from user.models import User
from user.forms import FormularioUser
from user.serializers import SerializadorGerenciarUser, SerializadorUser
from PetLar.mixins import AdminRequiredMixin

# Create your views here.
class ListarUsuarios(AdminRequiredMixin, ListView):
    # view para listar usuários cadastrados
    model = User
    template_name = 'user/listar_usuarios.html'
    context_object_name = 'usuarios'

    def get_queryset(self, **kwargs):
        pesquisa = self.request.GET.get('pesquisa')
        queryset = User.objects.all()
        if pesquisa is not None:
            queryset = queryset.filter(nome__icontains=pesquisa)
        return queryset
    

class ListarOngsPendentes(AdminRequiredMixin, ListView):
    # view para listar ONGs aguardando aprovação
    model = User
    template_name = 'user/listar_ongs_pendentes.html'
    context_object_name = 'usuarios'

    def get_queryset(self, **kwargs):
        return User.objects.filter(
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_PENDENTE,
        ).order_by('nome')


class CriarUsuario(AdminRequiredMixin, CreateView):
    # view para criar um novo usuário
    model = User
    form_class = FormularioUser
    template_name = 'user/novo_usuario.html'
    success_url = reverse_lazy('listar_usuarios')

    def form_valid(self, form):
        response = super().form_valid(form)
        email = self.object.email
        senha = form.cleaned_data.get('senha')
        if not AuthUser.objects.filter(username=email).exists():
            AuthUser.objects.create_user(username=email, email=email, password=senha)
        return response


class CadastroUsuario(CreateView):
    # view para cadastro público de usuário
    model = User
    form_class = FormularioUser
    template_name = 'user/cadastro_usuario.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['require_ong_documents'] = True
        kwargs['show_verification_status'] = False
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home_pets')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if form.cleaned_data.get('tipo_usuario') == TIPO_ONG:
            form.instance.status_verificacao_ong = STATUS_ONG_PENDENTE
        else:
            form.instance.status_verificacao_ong = STATUS_ONG_NAO_SE_APLICA
        response = super().form_valid(form)
        email = self.object.email
        senha = form.cleaned_data.get('senha')
        auth_user, created = AuthUser.objects.get_or_create(username=email, defaults={'email': email})
        auth_user.email = email
        auth_user.set_password(senha)
        auth_user.save()
        login(self.request, auth_user)
        return response

    def get_success_url(self):
        return reverse_lazy('home_pets')


class EditarUsuario(AdminRequiredMixin, UpdateView):
    # view para editar um usuário existente
    model = User
    form_class = FormularioUser
    template_name = 'user/editar_usuario.html'
    success_url = reverse_lazy('listar_usuarios')

    def form_valid(self, form):
        obj = self.get_object()
        old_email = obj.email
        senha = form.cleaned_data.get('senha')
        if not senha:
            form.instance.senha = obj.senha
        response = super().form_valid(form)
        new_email = self.object.email
        auth_user = AuthUser.objects.filter(username=old_email).first()
        if auth_user:
            auth_user.username = new_email
            auth_user.email = new_email
            if senha:
                auth_user.set_password(senha)
            auth_user.save()
        else:
            AuthUser.objects.create_user(username=new_email, email=new_email, password=senha or self.object.senha)
        return response


class DeletarUsuario(AdminRequiredMixin, DeleteView):
    # view para deletar um usuário existente
    model = User
    template_name = 'user/deletar_usuario.html'
    success_url = reverse_lazy('listar_usuarios')

    def form_valid(self, form):
        AuthUser.objects.filter(username=self.object.email).delete()
        return super().form_valid(form)


class APIListarUsuarios(ListAPIView):
    # view para listar instâncias de usuários por meio de API REST
    serializer_class = SerializadorUser
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.none()


class APIGerenciarUsuarios(ListCreateAPIView):
    # view para listar e criar usuários por meio de API REST
    serializer_class = SerializadorGerenciarUser
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pesquisa = self.request.GET.get('pesquisa')
        queryset = User.objects.all().order_by('nome')

        if not self.request.user.is_superuser:
            return queryset.none()

        if pesquisa is not None:
            queryset = queryset.filter(nome__icontains=pesquisa)
        return queryset

    def perform_create(self, serializer):
        usuario = serializer.save()
        senha = serializer.validated_data.get('senha') or usuario.senha
        auth_user, created = AuthUser.objects.get_or_create(
            username=usuario.email,
            defaults={'email': usuario.email},
        )
        auth_user.email = usuario.email
        auth_user.set_password(senha)
        auth_user.save()


class APIEditarUsuario(RetrieveUpdateDestroyAPIView):
    # view para editar e deletar usuários por meio de API REST
    serializer_class = SerializadorGerenciarUser
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = User.objects.all()

        if self.request.user.is_superuser:
            return queryset

        return queryset.none()

    def perform_update(self, serializer):
        usuario_antigo = self.get_object()
        email_antigo = usuario_antigo.email
        usuario = serializer.save()
        senha = serializer.validated_data.get('senha')

        auth_user = AuthUser.objects.filter(username=email_antigo).first()
        if auth_user:
            auth_user.username = usuario.email
            auth_user.email = usuario.email
            if senha:
                auth_user.set_password(senha)
            auth_user.save()
        else:
            AuthUser.objects.create_user(username=usuario.email, email=usuario.email, password=senha or usuario.senha)

    def perform_destroy(self, instance):
        AuthUser.objects.filter(username=instance.email).delete()
        instance.delete()
