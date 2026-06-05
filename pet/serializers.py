from rest_framework.serializers import ModelSerializer, SerializerMethodField

from pet.models import Pet


class SerializadorPet(ModelSerializer):
    nome_sexo = SerializerMethodField()
    nome_porte = SerializerMethodField()
    nome_status = SerializerMethodField()
    idade_texto = SerializerMethodField()
    nome_responsavel = SerializerMethodField()

    class Meta:
        model = Pet
        fields = [
            'id',
            'nome',
            'especie',
            'raca',
            'idade',
            'idade_texto',
            'sexo',
            'nome_sexo',
            'porte',
            'nome_porte',
            'vacinado',
            'castrado',
            'descricao',
            'status',
            'nome_status',
            'nome_responsavel',
            'data_cadastro',
        ]

    def get_nome_sexo(self, instancia):
        return instancia.get_sexo_display()

    def get_nome_porte(self, instancia):
        return instancia.get_porte_display()

    def get_nome_status(self, instancia):
        return instancia.get_status_display()

    def get_idade_texto(self, instancia):
        return instancia.idade_formatada

    def get_nome_responsavel(self, instancia):
        if instancia.responsavel:
            return instancia.responsavel.nome
        return None
