from rest_framework.serializers import ModelSerializer, SerializerMethodField

from solicitacao.models import SolicitacaoDeAdocao


class SerializadorSolicitacaoDeAdocao(ModelSerializer):
    nome_adotante = SerializerMethodField()
    telefone_adotante = SerializerMethodField()
    nome_pet = SerializerMethodField()
    nome_status = SerializerMethodField()

    class Meta:
        model = SolicitacaoDeAdocao
        fields = [
            'id',
            'adotante',
            'nome_adotante',
            'telefone_adotante',
            'pet',
            'nome_pet',
            'status',
            'nome_status',
            'mensagem',
            'data_solicitacao',
        ]

    def get_nome_adotante(self, instancia):
        return instancia.adotante.nome

    def get_telefone_adotante(self, instancia):
        return instancia.adotante.telefone

    def get_nome_pet(self, instancia):
        return instancia.pet.nome

    def get_nome_status(self, instancia):
        return instancia.get_status_display()
