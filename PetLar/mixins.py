from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from user.utils import get_custom_user_for_request


class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_superuser:
            return redirect('home_pets')

        return super().dispatch(request, *args, **kwargs)


class PetManagerRequiredMixin(LoginRequiredMixin):
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
