from django.db import models

from pet.models import Pet
from solicitacao.consts import OPCOES_STATUS_SOLICITACAO
from user.models import User


class SolicitacaoDeAdocao(models.Model):
    id = models.AutoField(primary_key=True)
    adotante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='solicitacoes',
    )
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name='solicitacoes',
    )
    status = models.CharField(
        max_length=20,
        choices=OPCOES_STATUS_SOLICITACAO,
        default='PENDENTE',
    )
    mensagem = models.TextField()
    data_solicitacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['adotante', 'pet'],
                name='solicitacao_unica_por_adotante_pet',
            )
        ]
        ordering = ['-data_solicitacao']

    def __str__(self):
        return f'{self.adotante.nome} - {self.pet.nome}'
