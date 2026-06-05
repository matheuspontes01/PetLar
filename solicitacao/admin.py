from django.contrib import admin

from solicitacao.models import SolicitacaoDeAdocao


class SolicitacaoDeAdocaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'adotante', 'pet', 'status', 'data_solicitacao')
    list_filter = ('status', 'data_solicitacao')
    search_fields = ('adotante__nome', 'pet__nome', 'mensagem')


admin.site.register(SolicitacaoDeAdocao, SolicitacaoDeAdocaoAdmin)
