from django.views.generic import View
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as AuthUser
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from user.models import User as CustomUser
from PetLar.mixins import get_custom_user_for_request

class Login(View):
    def get_post_login_redirect_name(self, auth_user=None):
        if auth_user and auth_user.is_superuser:
            return 'listar_usuarios'

        return 'home_pets'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(self.get_post_login_redirect_name(request.user))
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
                return redirect(self.get_post_login_redirect_name(user))
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
        usuario = request.data.get('username')
        senha = request.data.get('password')

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
                auth_user, created = AuthUser.objects.get_or_create(
                    username=custom.email,
                    defaults={'email': custom.email},
                )
                if created or not auth_user.check_password(senha):
                    auth_user.email = custom.email
                    auth_user.set_password(senha)
                    auth_user.save()

                user = authenticate(request, username=auth_user.username, password=senha)

        if user is None:
            return Response(
                {'detail': 'Usuário, e-mail ou senha inválidos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, created = Token.objects.get_or_create(user=user)

        if user.is_superuser:
            return Response({
                'id': user.id,
                'nome': user.first_name or user.username,
                'email': user.email,
                'token': token.key,
                'tipo_usuario': 'ADMINISTRADOR',
                'nome_tipo_usuario': 'Administrador',
                'ong_aprovada': False,
                'is_superuser': True,
            })

        custom_user = get_custom_user_for_request(request)
        if not custom_user and user.email:
            custom_user = CustomUser.objects.filter(email=user.email).first()

        return Response({
            'id': user.id,
            'nome': user.first_name or user.username,
            'email': user.email,
            'token': token.key,
            'tipo_usuario': custom_user.tipo_usuario if custom_user else '',
            'nome_tipo_usuario': custom_user.get_tipo_usuario_display() if custom_user else 'Administrador',
            'ong_aprovada': custom_user.ong_aprovada if custom_user else False,
            'is_superuser': user.is_superuser,
        })
        
