from django.views.generic import View
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as AuthUser

from user.models import User as CustomUser
from user.utils import get_custom_user_for_request, get_post_login_redirect_name

class Login(View):
    def get(self, request):
        if request.user.is_authenticated:
            custom_user = get_custom_user_for_request(request)
            return redirect(get_post_login_redirect_name(custom_user))
        contexto = {}
        return render(request, 'autenticacao.html', contexto)
    
    def post(self, request):
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        # Try normal Django auth first (username is email)
        user = authenticate(request, username=email, password=senha)

        if user is None:
            # Fallback: try to match the custom User model (password stored in 'senha')
            try:
                custom = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                custom = None

            if custom and custom.senha == senha:
                # Ensure an AuthUser exists and has this password
                auth_user, created = AuthUser.objects.get_or_create(username=email, defaults={'email': email})
                if created:
                    auth_user.set_password(senha)
                    auth_user.save()
                else:
                    # if password doesn't match, update it to match custom (so authenticate works)
                    if not auth_user.check_password(senha):
                        auth_user.set_password(senha)
                        auth_user.save()

                # Now authenticate again
                user = authenticate(request, username=email, password=senha)

        if user is not None:
            if user.is_active:
                login(request, user)
                custom_user = CustomUser.objects.filter(email=email).first()
                return redirect(get_post_login_redirect_name(custom_user))
            else:
                return render(request, 'autenticacao.html', {'mensagem': 'Usuário inativo.'})
        else:
            return render(request, 'autenticacao.html', {'mensagem': 'Email ou senha inválidos.'})


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('login')
        