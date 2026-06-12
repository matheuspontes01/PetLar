from rest_framework.serializers import ModelSerializer, SerializerMethodField

from user.models import User


class SerializadorUser(ModelSerializer):
    nome_tipo_usuario = SerializerMethodField()
    nome_status_verificacao_ong = SerializerMethodField()

    class Meta:
        model = User
        exclude = ['senha']

    def get_nome_tipo_usuario(self, instancia):
        return instancia.get_tipo_usuario_display()

    def get_nome_status_verificacao_ong(self, instancia):
        return instancia.get_status_verificacao_ong_display()


class SerializadorGerenciarUser(ModelSerializer):
    nome_tipo_usuario = SerializerMethodField()
    nome_status_verificacao_ong = SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'nome',
            'email',
            'senha',
            'telefone',
            'tipo_usuario',
            'nome_tipo_usuario',
            'razao_social_ong',
            'cnpj_ong',
            'status_verificacao_ong',
            'nome_status_verificacao_ong',
            'data_criacao',
        ]
        extra_kwargs = {
            'senha': {'write_only': True, 'required': False, 'allow_blank': True},
            'telefone': {'required': False, 'allow_blank': True, 'allow_null': True},
            'razao_social_ong': {'required': False, 'allow_blank': True, 'allow_null': True},
            'cnpj_ong': {'required': False, 'allow_blank': True, 'allow_null': True},
            'status_verificacao_ong': {'required': False},
        }

    def get_nome_tipo_usuario(self, instancia):
        return instancia.get_tipo_usuario_display()

    def get_nome_status_verificacao_ong(self, instancia):
        return instancia.get_status_verificacao_ong_display()
