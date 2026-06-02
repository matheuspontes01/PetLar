from django.db import models
from pet.consts import *

# Create your models here.
class Pet(models.Model):

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    especie = models.CharField(max_length=100)
    fotos = models.ImageField(upload_to='pets/')
    raca = models.CharField(max_length=100)
    idade = models.IntegerField(verbose_name='Idade (meses)')
    sexo = models.CharField(max_length=20, choices=OPCOES_SEXO)
    porte = models.CharField(max_length=20, choices=OPCOES_PORTE)
    vacinado = models.BooleanField(default=False)
    castrado = models.BooleanField(default=False)
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=OPCOES_STATUS, default='1')
    responsavel = models.ForeignKey(
        'user.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pets',
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    @property
    def idade_formatada(self):
        if self.idade <= 0:
            return 'Menos de 1 mês'

        anos = self.idade // 12
        meses = self.idade % 12
        partes = []

        if anos:
            partes.append(f'{anos} ano' if anos == 1 else f'{anos} anos')
        if meses:
            partes.append(f'{meses} mês' if meses == 1 else f'{meses} meses')

        return ' e '.join(partes)

    @property
    def whatsapp_url(self):
        if not self.responsavel or not self.responsavel.telefone:
            return None

        telefone = ''.join(ch for ch in self.responsavel.telefone if ch.isdigit())
        if len(telefone) == 10 or len(telefone) == 11:
            telefone = f'55{telefone}'

        mensagem = (
            f'Olá! Vi o pet {self.nome} no PetLar e gostaria de mais informações '
            f'sobre a adoção.'
        )
        from urllib.parse import quote

        return f'https://wa.me/{telefone}?text={quote(mensagem)}'
