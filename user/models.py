from django.db import models

class User(models.Model):
    class TipoUsuario(models.TextChoices):
        ADOTANTE = "ADOTANTE", "Adotante"
        ONG = "ONG", "ONG"
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"

    class StatusVerificacaoONG(models.TextChoices):
        NAO_SE_APLICA = "NAO_SE_APLICA", "Não se aplica"
        PENDENTE = "PENDENTE", "Pendente"
        APROVADA = "APROVADA", "Aprovada"
        REJEITADA = "REJEITADA", "Rejeitada"

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TipoUsuario.choices,
        default=TipoUsuario.ADOTANTE,
    )
    razao_social_ong = models.CharField(max_length=255, blank=True, null=True)
    cnpj_ong = models.CharField(max_length=18, blank=True, null=True)
    comprovante_ong = models.FileField(upload_to='comprovantes_ongs/', blank=True, null=True)
    status_verificacao_ong = models.CharField(
        max_length=20,
        choices=StatusVerificacaoONG.choices,
        default=StatusVerificacaoONG.NAO_SE_APLICA,
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    @property
    def ong_aprovada(self):
        return (
            self.tipo_usuario == self.TipoUsuario.ONG
            and self.status_verificacao_ong == self.StatusVerificacaoONG.APROVADA
        )
