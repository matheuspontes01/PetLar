from user.utils import can_manage_pets, get_custom_user_for_request


def user_profile(request):
    custom_user = get_custom_user_for_request(request)
    return {
        'perfil_usuario': custom_user,
        'is_admin_profile': bool(request.user.is_authenticated and request.user.is_superuser),
        'can_manage_pets': can_manage_pets(request),
    }
