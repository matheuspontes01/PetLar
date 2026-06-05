from user.consts import TIPO_ONG
from user.models import User as CustomUser


def get_custom_user_for_request(request):
    if not request.user.is_authenticated:
        return None

    email = getattr(request.user, 'email', '')
    if not email:
        return None

    return CustomUser.objects.filter(email=email).first()


def is_admin_profile(request):
    return bool(request.user.is_authenticated and request.user.is_superuser)


def can_manage_pets(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return True

    custom_user = get_custom_user_for_request(request)
    return bool(
        custom_user
        and (
            custom_user.tipo_usuario == TIPO_ONG
            and custom_user.ong_aprovada
        )
    )


def get_post_login_redirect_name(custom_user, auth_user=None):
    if auth_user and auth_user.is_superuser:
        return 'listar_usuarios'

    return 'home_pets'
