from django.contrib.auth.models import User as AuthUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token

from pet.models import Pet
from solicitacao.forms import FormularioAvaliacaoSolicitacao, FormularioSolicitacao
from solicitacao.models import SolicitacaoDeAdocao
from user.consts import *
from user.models import User


def imagem_teste(nome='pet.jpg'):
    imagem = (
        b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\xff\xff\xff,'
        b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
    )
    return SimpleUploadedFile(nome, imagem, content_type='image/gif')


class TestesModelSolicitacao(TestCase):
    # Classe de testes para o modelo SolicitacaoDeAdocao

    def setUp(self):
        self.adotante = User.objects.create(nome='Ana', email='ana@petlar.com', senha='12345', tipo_usuario=TIPO_ADOTANTE)
        self.ong = User.objects.create(
            nome='ONG PetLar',
            email='ong@petlar.com',
            senha='12345',
            telefone='63999999999',
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_APROVADA,
        )
        self.pet = Pet.objects.create(
            nome='Thor',
            especie='Cão',
            fotos=imagem_teste(),
            raca='Vira-lata',
            idade=12,
            sexo='1',
            porte='1',
            descricao='Pet dócil',
            status='1',
            responsavel=self.ong,
        )
        self.solicitacao = SolicitacaoDeAdocao.objects.create(
            adotante=self.adotante,
            pet=self.pet,
            mensagem='Tenho interesse na adoção.',
        )

    def test_str(self):
        self.assertEqual(str(self.solicitacao), 'Ana - Thor')


class TestesFormularioSolicitacao(TestCase):
    # Classe de testes para os formulários de solicitação

    def test_formulario_solicitacao_valido(self):
        form = FormularioSolicitacao(data={'mensagem': 'Quero adotar este pet.'})
        self.assertTrue(form.is_valid())

    def test_formulario_avaliacao_valido(self):
        form = FormularioAvaliacaoSolicitacao(data={'status': 'APROVADA'})
        self.assertTrue(form.is_valid())


class TestesViewSolicitacao(TestCase):
    # Classe de testes para as views de solicitação

    def setUp(self):
        self.adotante = User.objects.create(
            nome='Ana',
            email='ana@petlar.com',
            senha='12345',
            telefone='63999999999',
            tipo_usuario=TIPO_ADOTANTE,
        )
        self.auth_adotante = AuthUser.objects.create_user(username='ana@petlar.com', email='ana@petlar.com', password='12345')

        self.ong = User.objects.create(
            nome='ONG PetLar',
            email='ong@petlar.com',
            senha='12345',
            telefone='63999999999',
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_APROVADA,
        )
        self.auth_ong = AuthUser.objects.create_user(username='ong@petlar.com', email='ong@petlar.com', password='12345')

        self.pet = Pet.objects.create(
            nome='Thor',
            especie='Cão',
            fotos=imagem_teste(),
            raca='Vira-lata',
            idade=12,
            sexo='1',
            porte='1',
            descricao='Pet dócil',
            status='1',
            responsavel=self.ong,
        )

    def test_criar_solicitacao(self):
        self.client.force_login(self.auth_adotante)
        url = reverse('criar_solicitacao', kwargs={'pet_pk': self.pet.pk})
        response = self.client.post(url, {'mensagem': 'Tenho interesse na adoção.'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_solicitacoes'))
        self.assertEqual(SolicitacaoDeAdocao.objects.count(), 1)

    def test_listar_solicitacoes_adotante(self):
        SolicitacaoDeAdocao.objects.create(adotante=self.adotante, pet=self.pet, mensagem='Tenho interesse.')
        self.client.force_login(self.auth_adotante)
        response = self.client.get(reverse('listar_solicitacoes'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context.get('solicitacoes')), 1)

    def test_aprovar_solicitacao(self):
        solicitacao = SolicitacaoDeAdocao.objects.create(adotante=self.adotante, pet=self.pet, mensagem='Tenho interesse.')
        self.client.force_login(self.auth_ong)
        url = reverse('editar_solicitacao', kwargs={'pk': solicitacao.pk})
        response = self.client.post(url, {'status': 'APROVADA'})
        self.assertEqual(response.status_code, 302)
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.status, '3')

    def test_cancelar_solicitacao(self):
        solicitacao = SolicitacaoDeAdocao.objects.create(adotante=self.adotante, pet=self.pet, mensagem='Tenho interesse.')
        self.client.force_login(self.auth_adotante)
        url = reverse('deletar_solicitacao', kwargs={'pk': solicitacao.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SolicitacaoDeAdocao.objects.count(), 0)


class TestesViewEditarSolicitacao(TestCase):
    # Classe de testes para a view EditarSolicitacao

    def setUp(self):
        self.adotante = User.objects.create(nome='Ana', email='ana@petlar.com', senha='12345', tipo_usuario=TIPO_ADOTANTE)
        self.ong = User.objects.create(
            nome='ONG PetLar',
            email='ong@petlar.com',
            senha='12345',
            telefone='63999999999',
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_APROVADA,
        )
        self.auth_ong = AuthUser.objects.create_user(username='ong@petlar.com', email='ong@petlar.com', password='12345')
        self.client.force_login(self.auth_ong)
        self.pet = Pet.objects.create(
            nome='Thor',
            especie='Cão',
            fotos=imagem_teste(),
            raca='Vira-lata',
            idade=12,
            sexo='1',
            porte='1',
            descricao='Pet dócil',
            status='1',
            responsavel=self.ong,
        )
        self.instancia = SolicitacaoDeAdocao.objects.create(
            adotante=self.adotante,
            pet=self.pet,
            mensagem='Tenho interesse.',
        )
        self.url = reverse('editar_solicitacao', kwargs={'pk': self.instancia.pk})

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context.get('object'), SolicitacaoDeAdocao)
        self.assertIsInstance(response.context.get('form'), FormularioAvaliacaoSolicitacao)
        self.assertEqual(response.context.get('object').pk, self.instancia.pk)

    def test_post(self):
        response = self.client.post(self.url, {'status': 'REJEITADA'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_solicitacoes'))
        self.instancia.refresh_from_db()
        self.assertEqual(self.instancia.status, 'REJEITADA')


class TestesViewDeletarSolicitacao(TestCase):
    # Classe de testes para a view DeletarSolicitacao

    def setUp(self):
        self.adotante = User.objects.create(nome='Ana', email='ana@petlar.com', senha='12345', tipo_usuario=TIPO_ADOTANTE)
        self.auth_adotante = AuthUser.objects.create_user(username='ana@petlar.com', email='ana@petlar.com', password='12345')
        self.ong = User.objects.create(
            nome='ONG PetLar',
            email='ong@petlar.com',
            senha='12345',
            telefone='63999999999',
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_APROVADA,
        )
        self.pet = Pet.objects.create(
            nome='Thor',
            especie='Cão',
            fotos=imagem_teste(),
            raca='Vira-lata',
            idade=12,
            sexo='1',
            porte='1',
            descricao='Pet dócil',
            status='1',
            responsavel=self.ong,
        )
        self.instancia = SolicitacaoDeAdocao.objects.create(
            adotante=self.adotante,
            pet=self.pet,
            mensagem='Tenho interesse.',
        )
        self.client.force_login(self.auth_adotante)
        self.url = reverse('deletar_solicitacao', kwargs={'pk': self.instancia.pk})

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context.get('object'), SolicitacaoDeAdocao)
        self.assertEqual(response.context.get('object').pk, self.instancia.pk)

    def test_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_solicitacoes'))
        self.assertEqual(SolicitacaoDeAdocao.objects.count(), 0)


class TestesAPIListarSolicitacoes(TestCase):
    # Classe de testes para a API de listagem de solicitações

    def setUp(self):
        self.adotante = User.objects.create(
            nome='Ana',
            email='ana@petlar.com',
            senha='12345',
            telefone='63999999999',
            tipo_usuario=TIPO_ADOTANTE,
        )
        self.auth_adotante = AuthUser.objects.create_user(username='ana@petlar.com', email='ana@petlar.com', password='12345')
        self.token = Token.objects.create(user=self.auth_adotante)
        self.ong = User.objects.create(
            nome='ONG PetLar',
            email='ong@petlar.com',
            senha='12345',
            telefone='63999999999',
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_APROVADA,
        )
        self.pet = Pet.objects.create(
            nome='Thor',
            especie='Cão',
            fotos=imagem_teste(),
            raca='Vira-lata',
            idade=12,
            sexo='1',
            porte='1',
            descricao='Pet dócil',
            status='1',
            responsavel=self.ong,
        )
        SolicitacaoDeAdocao.objects.create(adotante=self.adotante, pet=self.pet, mensagem='Tenho interesse.')
        self.url = reverse('api_listar_solicitacoes')

    def test_get(self):
        response = self.client.get(self.url, HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
