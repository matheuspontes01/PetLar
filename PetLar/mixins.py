from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from user.consts import STATUS_ONG_PENDENTE, TIPO_ONG
from user.models import User as CustomUser


def get_custom_user_for_request(request):
    if not request.user.is_authenticated:
        return None

    email = getattr(request.user, 'email', '')
    if not email:
        return None

    return CustomUser.objects.filter(email=email).first()


class PerfilUsuarioMixin:
    def get_perfil_usuario(self):
        return get_custom_user_for_request(self.request)

    def usuario_pode_gerenciar_pets(self, perfil_usuario):
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            return True

        return bool(
            perfil_usuario
            and perfil_usuario.tipo_usuario == TIPO_ONG
            and perfil_usuario.ong_aprovada
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfil_usuario = self.get_perfil_usuario()
        context['perfil_usuario'] = perfil_usuario
        context['is_admin_profile'] = bool(
            self.request.user.is_authenticated
            and self.request.user.is_superuser
        )
        context['can_manage_pets'] = self.usuario_pode_gerenciar_pets(perfil_usuario)
        context['ongs_pendentes_count'] = CustomUser.objects.filter(
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_PENDENTE,
        ).count()
        context['solicitacoes_pendentes_ong_count'] = self.get_solicitacoes_pendentes_ong_count(
            perfil_usuario
        )
        return context

    def get_solicitacoes_pendentes_ong_count(self, perfil_usuario):
        if not (
            perfil_usuario
            and perfil_usuario.tipo_usuario == TIPO_ONG
            and perfil_usuario.ong_aprovada
        ):
            return 0

        from solicitacao.models import SolicitacaoDeAdocao

        return SolicitacaoDeAdocao.objects.filter(
            pet__responsavel=perfil_usuario,
            status='PENDENTE',
        ).count()


class AdminRequiredMixin(PerfilUsuarioMixin, LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_superuser:
            return redirect('home_pets')

        return super().dispatch(request, *args, **kwargs)


class PetManagerRequiredMixin(PerfilUsuarioMixin, LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        custom_user = get_custom_user_for_request(request)
        if request.user.is_superuser:
            self.custom_user = custom_user
            return super().dispatch(request, *args, **kwargs)

        if not custom_user:
            return redirect('home_pets')

        can_manage = custom_user.ong_aprovada
        if not can_manage:
            return redirect('home_pets')

        self.custom_user = custom_user
        return super().dispatch(request, *args, **kwargs)
