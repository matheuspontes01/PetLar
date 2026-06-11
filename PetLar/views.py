from django.views.generic import View
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as AuthUser
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from user.models import User as CustomUser
from user.utils import get_custom_user_for_request, get_post_login_redirect_name

class Login(View):
    def get(self, request):
        if request.user.is_authenticated:
            custom_user = get_custom_user_for_request(request)
            return redirect(get_post_login_redirect_name(custom_user, request.user))
        contexto = {}
        return render(request, 'autenticacao.html', contexto)
    
    def post(self, request):
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')

        username = usuario
        auth_user = AuthUser.objects.filter(email=usuario).first()
        if auth_user:
            username = auth_user.username

        user = authenticate(request, username=username, password=senha)

        if user is None:
            try:
                custom = CustomUser.objects.get(email=usuario)
            except CustomUser.DoesNotExist:
                custom = None

            if custom and custom.senha == senha:
                auth_user, created = AuthUser.objects.get_or_create(username=custom.email, defaults={'email': custom.email})
                if created:
                    auth_user.set_password(senha)
                    auth_user.save()
                else:
                    if not auth_user.check_password(senha):
                        auth_user.set_password(senha)
                        auth_user.save()

                user = authenticate(request, username=auth_user.username, password=senha)

        if user is not None:
            if user.is_active:
                login(request, user)
                custom_user = get_custom_user_for_request(request)
                return redirect(get_post_login_redirect_name(custom_user, user))
            else:
                return render(request, 'autenticacao.html', {'mensagem': 'Usuário inativo.'})
        else:
            return render(request, 'autenticacao.html', {'mensagem': 'Usuário, e-mail ou senha inválidos.'})


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('login')


class LoginAPI(ObtainAuthToken):
    # view para autenticação de usuários por meio de API REST
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={
                'request': request,
            },
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'id': user.id,
            'nome': user.first_name or user.username,
            'email': user.email,
            'token': token.key,
        })
        
