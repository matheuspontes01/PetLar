from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from user.models import User as CustomUser
from user.utils import get_custom_user_for_request


class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if response is not None:
            return response

        custom_user = get_custom_user_for_request(request)
        if not custom_user or custom_user.tipo_usuario != CustomUser.TipoUsuario.ADMINISTRADOR:
            return redirect('home_pets')

        return super().dispatch(request, *args, **kwargs)