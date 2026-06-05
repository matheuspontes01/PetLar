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
