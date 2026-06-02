from django.contrib import admin

from user.models import User

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'email', 'tipo_usuario', 'status_verificacao_ong', 'data_criacao')
    list_filter = ('tipo_usuario', 'status_verificacao_ong')
    search_fields = ('nome', 'email', 'razao_social_ong', 'cnpj_ong')


admin.site.register(User, UserAdmin)
