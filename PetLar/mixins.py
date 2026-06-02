from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from user.models import User as CustomUser
from user.utils import get_custom_user_for_request


class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        custom_user = get_custom_user_for_request(request)
        if not custom_user or custom_user.tipo_usuario != CustomUser.TipoUsuario.ADMINISTRADOR:
            return redirect('home_pets')

        return super().dispatch(request, *args, **kwargs)


class PetManagerRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        custom_user = get_custom_user_for_request(request)
        if not custom_user:
            return redirect('home_pets')

        can_manage = (
            custom_user.tipo_usuario == CustomUser.TipoUsuario.ADMINISTRADOR
            or custom_user.ong_aprovada
        )
        if not can_manage:
            return redirect('home_pets')

        self.custom_user = custom_user
        return super().dispatch(request, *args, **kwargs)
