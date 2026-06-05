from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_superuser:
            return redirect('home_pets')

        return super().dispatch(request, *args, **kwargs)
