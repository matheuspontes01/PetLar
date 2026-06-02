from user.models import User as CustomUser


def get_custom_user_for_request(request):
    if not request.user.is_authenticated:
        return None

    email = getattr(request.user, 'email', '')
    if not email:
        return None

    return CustomUser.objects.filter(email=email).first()


def is_admin_profile(request):
    custom_user = get_custom_user_for_request(request)
    return bool(custom_user and custom_user.tipo_usuario == CustomUser.TipoUsuario.ADMINISTRADOR)


def can_manage_pets(request):
    custom_user = get_custom_user_for_request(request)
    return bool(
        custom_user
        and (
            custom_user.tipo_usuario == CustomUser.TipoUsuario.ADMINISTRADOR
            or custom_user.ong_aprovada
        )
    )


def get_post_login_redirect_name(custom_user):
    if custom_user and custom_user.tipo_usuario == CustomUser.TipoUsuario.ADMINISTRADOR:
        return 'listar_usuarios'
    return 'home_pets'
