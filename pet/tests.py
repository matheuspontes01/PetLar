from django.contrib.auth.models import User as AuthUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token

from pet.forms import FormularioPet
from pet.models import Pet
from user.consts import *
from user.models import User


def imagem_teste(nome='pet.jpg'):
    imagem = (
        b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\xff\xff\xff,'
        b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
    )
    return SimpleUploadedFile(nome, imagem, content_type='image/gif')


class TestesModelPet(TestCase):
    # Classe de testes para o modelo Pet

    def setUp(self):
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
            idade=14,
            sexo='1',
            porte='1',
            descricao='Pet dócil',
            status='1',
            responsavel=self.ong,
        )

    def test_idade_formatada(self):
        self.assertEqual(self.pet.idade_formatada, '1 ano e 2 meses')
        self.pet.idade = 1
        self.assertEqual(self.pet.idade_formatada, '1 mês')

    def test_whatsapp_url(self):
        self.assertIn('wa.me', self.pet.whatsapp_url)


class TestesFormularioPet(TestCase):
    # Classe de testes para o formulário de pet

    def setUp(self):
        self.ong = User.objects.create(
            nome='ONG PetLar',
            email='ong@petlar.com',
            senha='12345',
            telefone='63999999999',
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_APROVADA,
        )

    def test_formulario_admin_possui_responsavel(self):
        form = FormularioPet()
        self.assertIn('responsavel', form.fields)

    def test_formulario_ong_remove_responsavel(self):
        form = FormularioPet(current_user=self.ong)
        self.assertNotIn('responsavel', form.fields)


class TestesViewListarPets(TestCase):
    # Classe de testes para a view ListarPets

    def setUp(self):
        self.auth_user = AuthUser.objects.create_superuser(username='admin', email='admin@petlar.com', password='12345')
        self.client.force_login(self.auth_user)
        self.url = reverse('listar_pets')
        self.ong = User.objects.create(
            nome='ONG PetLar',
            email='ong@petlar.com',
            senha='12345',
            telefone='63999999999',
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_APROVADA,
        )
        Pet.objects.create(
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

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context.get('pets')), 1)


class TestesViewDetalhePet(TestCase):
    # Classe de testes para a segurança da view DetalhePet

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
        self.auth_admin = AuthUser.objects.create_superuser(username='admin', email='admin@petlar.com', password='12345')
        self.pet_indisponivel = Pet.objects.create(
            nome='Thor',
            especie='Cão',
            fotos=imagem_teste(),
            raca='Vira-lata',
            idade=12,
            sexo='1',
            porte='1',
            descricao='Pet dócil',
            status='3',
            responsavel=self.ong,
        )
        self.url = reverse('detalhe_pet', kwargs={'pk': self.pet_indisponivel.pk})

    def test_adotante_nao_acessa_pet_indisponivel(self):
        self.client.force_login(self.auth_adotante)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_ong_responsavel_acessa_pet_indisponivel(self):
        self.client.force_login(self.auth_ong)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_superuser_acessa_pet_indisponivel(self):
        self.client.force_login(self.auth_admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class TestesViewCriarPet(TestCase):
    # Classe de testes para a view CriarPet

    def setUp(self):
        self.ong = User.objects.create(
            nome='ONG PetLar',
            email='ong@petlar.com',
            senha='12345',
            telefone='63999999999',
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_APROVADA,
        )
        self.auth_user = AuthUser.objects.create_user(username='ong@petlar.com', email='ong@petlar.com', password='12345')
        self.client.force_login(self.auth_user)
        self.url = reverse('criar_pet')

    def test_get_autenticado(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context.get('form'), FormularioPet)

    def test_post(self):
        dados = {
            'nome': 'Mel',
            'especie': 'Cão',
            'raca': 'Vira-lata',
            'idade': 8,
            'sexo': '2',
            'porte': '1',
            'descricao': 'Pet carinhosa',
            'status': '1',
        }
        response = self.client.post(self.url, {**dados, 'fotos': imagem_teste('mel.jpg')})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_pets'))
        self.assertEqual(Pet.objects.count(), 1)
        self.assertEqual(Pet.objects.first().responsavel, self.ong)


class TestesViewEditarPet(TestCase):
    # Classe de testes para a view EditarPet

    def setUp(self):
        self.ong = User.objects.create(
            nome='ONG PetLar',
            email='ong@petlar.com',
            senha='12345',
            telefone='63999999999',
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_APROVADA,
        )
        self.auth_user = AuthUser.objects.create_user(username='ong@petlar.com', email='ong@petlar.com', password='12345')
        self.client.force_login(self.auth_user)
        self.instancia = Pet.objects.create(
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
        self.url = reverse('editar_pet', kwargs={'pk': self.instancia.pk})

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context.get('object'), Pet)
        self.assertIsInstance(response.context.get('form'), FormularioPet)
        self.assertEqual(response.context.get('object').pk, self.instancia.pk)

    def test_post(self):
        dados = {
            'nome': 'Thor Editado',
            'especie': 'Cão',
            'raca': 'Vira-lata',
            'idade': 24,
            'sexo': '1',
            'porte': '2',
            'descricao': 'Pet dócil e brincalhão',
            'status': '1',
        }
        response = self.client.post(self.url, {**dados, 'fotos': imagem_teste('thor-editado.jpg')})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_pets'))
        self.instancia.refresh_from_db()
        self.assertEqual(self.instancia.nome, 'Thor Editado')
        self.assertEqual(self.instancia.idade, 24)


class TestesViewDeletarPet(TestCase):
    # Classe de testes para a view DeletarPet

    def setUp(self):
        self.ong = User.objects.create(
            nome='ONG PetLar',
            email='ong@petlar.com',
            senha='12345',
            telefone='63999999999',
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_APROVADA,
        )
        self.auth_user = AuthUser.objects.create_user(username='ong@petlar.com', email='ong@petlar.com', password='12345')
        self.client.force_login(self.auth_user)
        self.instancia = Pet.objects.create(
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
        self.url = reverse('deletar_pet', kwargs={'pk': self.instancia.pk})

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context.get('object'), Pet)
        self.assertEqual(response.context.get('object').pk, self.instancia.pk)

    def test_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_pets'))
        self.assertEqual(Pet.objects.count(), 0)


class TestesAPIListarPets(TestCase):
    # Classe de testes para a API de listagem de pets

    def setUp(self):
        self.auth_user = AuthUser.objects.create_user(username='api', email='api@petlar.com', password='12345')
        self.token = Token.objects.create(user=self.auth_user)
        self.ong = User.objects.create(
            nome='ONG PetLar',
            email='ong@petlar.com',
            senha='12345',
            telefone='63999999999',
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_APROVADA,
        )
        Pet.objects.create(
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
        self.url = reverse('api_listar_pets')

    def test_get(self):
        response = self.client.get(self.url, HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
