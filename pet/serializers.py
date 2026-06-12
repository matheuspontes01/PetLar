from rest_framework.serializers import ModelSerializer, SerializerMethodField

from pet.models import Pet
from user.consts import STATUS_ONG_APROVADA, TIPO_ONG
from user.models import User


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
            'fotos',
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


class SerializadorGerenciarPet(ModelSerializer):
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
            'fotos',
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
            'responsavel',
            'nome_responsavel',
            'data_cadastro',
        ]
        extra_kwargs = {
            'fotos': {'required': False, 'allow_null': True},
            'responsavel': {'required': False, 'allow_null': True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['responsavel'].queryset = User.objects.filter(
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_APROVADA,
        ).order_by('nome')

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
