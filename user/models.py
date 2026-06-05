from django.db import models
from user.consts import *

class User(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    tipo_usuario = models.CharField(
        max_length=20,
        choices=OPCOES_TIPO_USUARIO,
        default=TIPO_ADOTANTE,
    )
    razao_social_ong = models.CharField(max_length=255, blank=True, null=True)
    cnpj_ong = models.CharField(max_length=18, blank=True, null=True)
    comprovante_ong = models.FileField(upload_to='comprovantes_ongs/', blank=True, null=True)
    status_verificacao_ong = models.CharField(
        max_length=20,
        choices=OPCOES_STATUS_VERIFICACAO_ONG,
        default=STATUS_ONG_NAO_SE_APLICA,
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    @property
    def ong_aprovada(self):
        return (
            self.tipo_usuario == TIPO_ONG
            and self.status_verificacao_ong == STATUS_ONG_APROVADA
        )
