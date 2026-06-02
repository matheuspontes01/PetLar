from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.contrib.auth import login
from django.contrib.auth.models import User as AuthUser

from user.models import User
from user.forms import FormularioUser
from PetLar.mixins import AdminRequiredMixin

# Create your views here.
class ListarUsuarios(AdminRequiredMixin, ListView):
    model = User
    template_name = 'user/listar_usuarios.html'
    context_object_name = 'usuarios'

    def get_queryset(self, **kwargs):
        pesquisa = self.request.GET.get('pesquisa')
        queryset = User.objects.all()
        if pesquisa is not None:
            queryset = queryset.filter(nome__icontains=pesquisa)
        return queryset
    

class CriarUsuario(AdminRequiredMixin, CreateView):
    model = User
    form_class = FormularioUser
    template_name = 'user/novo_usuario.html'
    success_url = reverse_lazy('listar_usuarios')

    def form_valid(self, form):
        # save the custom user first
        response = super().form_valid(form)
        # create corresponding Django auth user (use email as username)
        email = self.object.email
        senha = form.cleaned_data.get('senha')
        if not AuthUser.objects.filter(username=email).exists():
            AuthUser.objects.create_user(username=email, email=email, password=senha)
        return response


class CadastroUsuario(CreateView):
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
        if form.cleaned_data.get('tipo_usuario') == User.TipoUsuario.ONG:
            form.instance.status_verificacao_ong = User.StatusVerificacaoONG.PENDENTE
        else:
            form.instance.status_verificacao_ong = User.StatusVerificacaoONG.NAO_SE_APLICA
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
    model = User
    form_class = FormularioUser
    template_name = 'user/editar_usuario.html'
    success_url = reverse_lazy('listar_usuarios')

    def form_valid(self, form):
        # capture old email before save
        obj = self.get_object()
        old_email = obj.email
        senha = form.cleaned_data.get('senha')
        response = super().form_valid(form)
        # update or create corresponding Django auth user
        new_email = self.object.email
        auth_user = AuthUser.objects.filter(username=old_email).first()
        if auth_user:
            auth_user.username = new_email
            auth_user.email = new_email
            if senha:
                auth_user.set_password(senha)
            auth_user.save()
        else:
            # create if not exists
            AuthUser.objects.create_user(username=new_email, email=new_email, password=senha)
        return response


class DeletarUsuario(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'user/deletar_usuario.html'
    success_url = reverse_lazy('listar_usuarios')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        # delete corresponding auth user
        AuthUser.objects.filter(username=obj.email).delete()
        return super().delete(request, *args, **kwargs)
