from django.contrib.auth.models import User as AuthUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token

from user.consts import *
from user.forms import FormularioUser
from user.models import User


class TestesModelUser(TestCase):
    # Classe de testes para o modelo User

    def setUp(self):
        self.ong = User.objects.create(
            nome='ONG PetLar',
            email='ong@petlar.com',
            senha='12345',
            telefone='63999999999',
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_APROVADA,
        )

    def test_ong_aprovada(self):
        self.assertTrue(self.ong.ong_aprovada)
        self.ong.status_verificacao_ong = STATUS_ONG_PENDENTE
        self.assertFalse(self.ong.ong_aprovada)


class TestesFormularioUser(TestCase):
    # Classe de testes para o formulário de usuário

    def test_formulario_adotante_valido(self):
        dados = {
            'nome': 'Maria',
            'email': 'maria@petlar.com',
            'senha': '12345',
            'telefone': '63999999999',
            'tipo_usuario': TIPO_ADOTANTE,
            'status_verificacao_ong': STATUS_ONG_NAO_SE_APLICA,
        }
        form = FormularioUser(data=dados)
        self.assertTrue(form.is_valid())

    def test_formulario_ong_exige_documentos(self):
        dados = {
            'nome': 'ONG Sem Documento',
            'email': 'ongsem@petlar.com',
            'senha': '12345',
            'telefone': '63999999999',
            'tipo_usuario': TIPO_ONG,
        }
        form = FormularioUser(data=dados, require_ong_documents=True, show_verification_status=False)
        self.assertFalse(form.is_valid())
        self.assertIn('cnpj_ong', form.errors)
        self.assertIn('comprovante_ong', form.errors)

    def test_formulario_ong_valido(self):
        dados = {
            'nome': 'ONG Completa',
            'email': 'ongcompleta@petlar.com',
            'senha': '12345',
            'telefone': '63999999999',
            'tipo_usuario': TIPO_ONG,
            'razao_social_ong': 'ONG Completa LTDA',
            'cnpj_ong': '04.252.011/0001-10',
        }
        arquivo = SimpleUploadedFile('comprovante.pdf', b'arquivo', content_type='application/pdf')
        form = FormularioUser(
            data=dados,
            files={'comprovante_ong': arquivo},
            require_ong_documents=True,
            show_verification_status=False,
        )
        self.assertTrue(form.is_valid())


class TestesViewListarUsuarios(TestCase):
    # Classe de testes para a view ListarUsuarios

    def setUp(self):
        self.auth_user = AuthUser.objects.create_superuser(
            username='admin',
            email='admin@petlar.com',
            password='12345',
        )
        self.client.force_login(self.auth_user)
        self.url = reverse('listar_usuarios')
        User.objects.create(nome='João', email='joao@petlar.com', senha='12345', tipo_usuario=TIPO_ADOTANTE)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context.get('usuarios')), User.objects.count())


class TestesViewListarOngsPendentes(TestCase):
    # Classe de testes para a view de ONGs pendentes

    def setUp(self):
        self.admin = AuthUser.objects.create_superuser(username='admin', email='admin@petlar.com', password='12345')
        self.client.force_login(self.admin)
        self.url = reverse('listar_ongs_pendentes')
        User.objects.create(
            nome='ONG Pendente',
            email='pendente@petlar.com',
            senha='12345',
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_PENDENTE,
        )
        User.objects.create(
            nome='ONG Aprovada',
            email='aprovada@petlar.com',
            senha='12345',
            tipo_usuario=TIPO_ONG,
            status_verificacao_ong=STATUS_ONG_APROVADA,
        )

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context.get('usuarios')), 1)
        self.assertEqual(response.context.get('usuarios')[0].status_verificacao_ong, STATUS_ONG_PENDENTE)


class TestesViewCadastroUsuario(TestCase):
    # Classe de testes para a view pública de cadastro de usuário

    def setUp(self):
        self.url = reverse('cadastro_usuario')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context.get('form'), FormularioUser)

    def test_get_nao_autenticado(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context.get('form'), FormularioUser)

    def test_post_adotante(self):
        dados = {
            'nome': 'Ana',
            'email': 'ana@petlar.com',
            'senha': '12345',
            'telefone': '63999999999',
            'tipo_usuario': TIPO_ADOTANTE,
        }
        response = self.client.post(self.url, dados)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(AuthUser.objects.filter(username='ana@petlar.com').exists())


class TestesViewEditarUsuario(TestCase):
    # Classe de testes para a view EditarUsuario

    def setUp(self):
        self.admin = AuthUser.objects.create_superuser(username='admin', email='admin@petlar.com', password='12345')
        self.client.force_login(self.admin)
        self.instancia = User.objects.create(
            nome='Carlos',
            email='carlos@petlar.com',
            senha='12345',
            telefone='63999999999',
            tipo_usuario=TIPO_ADOTANTE,
        )
        AuthUser.objects.create_user(username='carlos@petlar.com', email='carlos@petlar.com', password='12345')
        self.url = reverse('editar_usuario', kwargs={'pk': self.instancia.pk})

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context.get('object'), User)
        self.assertIsInstance(response.context.get('form'), FormularioUser)
        self.assertEqual(response.context.get('object').pk, self.instancia.pk)

    def test_post(self):
        dados = {
            'nome': 'Carlos Silva',
            'email': 'carlosnovo@petlar.com',
            'senha': '54321',
            'telefone': '63988888888',
            'tipo_usuario': TIPO_ADOTANTE,
            'status_verificacao_ong': STATUS_ONG_NAO_SE_APLICA,
        }
        response = self.client.post(self.url, dados)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_usuarios'))
        self.instancia.refresh_from_db()
        self.assertEqual(self.instancia.nome, 'Carlos Silva')
        self.assertTrue(AuthUser.objects.filter(username='carlosnovo@petlar.com').exists())

    def test_post_sem_senha_mantem_senha_atual(self):
        dados = {
            'nome': 'Carlos Sem Trocar Senha',
            'email': 'carlos@petlar.com',
            'senha': '',
            'telefone': '63988888888',
            'tipo_usuario': TIPO_ADOTANTE,
            'status_verificacao_ong': STATUS_ONG_NAO_SE_APLICA,
        }
        response = self.client.post(self.url, dados)

        self.assertEqual(response.status_code, 302)
        self.instancia.refresh_from_db()
        auth_user = AuthUser.objects.get(username='carlos@petlar.com')
        self.assertEqual(self.instancia.senha, '12345')
        self.assertTrue(auth_user.check_password('12345'))


class TestesViewDeletarUsuario(TestCase):
    # Classe de testes para a view DeletarUsuario

    def setUp(self):
        self.admin = AuthUser.objects.create_superuser(username='admin', email='admin@petlar.com', password='12345')
        self.client.force_login(self.admin)
        self.instancia = User.objects.create(
            nome='Carlos',
            email='carlos@petlar.com',
            senha='12345',
            tipo_usuario=TIPO_ADOTANTE,
        )
        AuthUser.objects.create_user(username='carlos@petlar.com', email='carlos@petlar.com', password='12345')
        self.url = reverse('deletar_usuario', kwargs={'pk': self.instancia.pk})

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context.get('object'), User)
        self.assertEqual(response.context.get('object').pk, self.instancia.pk)

    def test_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_usuarios'))
        self.assertEqual(User.objects.filter(pk=self.instancia.pk).count(), 0)
        self.assertFalse(AuthUser.objects.filter(username='carlos@petlar.com').exists())


class TestesAPIListarUsuarios(TestCase):
    # Classe de testes para a API de listagem de usuários

    def setUp(self):
        self.admin = AuthUser.objects.create_superuser(username='admin', email='admin@petlar.com', password='12345')
        self.token = Token.objects.create(user=self.admin)
        User.objects.create(nome='João', email='joao@petlar.com', senha='12345', tipo_usuario=TIPO_ADOTANTE)
        self.url = reverse('api_listar_usuarios')

    def test_get(self):
        response = self.client.get(self.url, HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), User.objects.count())


class TestesAPIGerenciarUsuarios(TestCase):
    # Classe de testes para a API de gerenciamento de usuários

    def setUp(self):
        self.admin = AuthUser.objects.create_superuser(username='admin', email='admin@petlar.com', password='12345')
        self.token = Token.objects.create(user=self.admin)
        self.url = reverse('api_gerenciar_usuarios')

    def test_post_cria_usuario_e_auth_user(self):
        dados = {
            'nome': 'Maria',
            'email': 'maria@petlar.com',
            'senha': '12345',
            'telefone': '63999999999',
            'tipo_usuario': TIPO_ADOTANTE,
            'status_verificacao_ong': STATUS_ONG_NAO_SE_APLICA,
        }
        response = self.client.post(
            self.url,
            dados,
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(AuthUser.objects.filter(username='maria@petlar.com').exists())

    def test_put_atualiza_usuario_e_auth_user(self):
        usuario = User.objects.create(
            nome='Carlos',
            email='carlos@petlar.com',
            senha='12345',
            tipo_usuario=TIPO_ADOTANTE,
            status_verificacao_ong=STATUS_ONG_NAO_SE_APLICA,
        )
        AuthUser.objects.create_user(username='carlos@petlar.com', email='carlos@petlar.com', password='12345')
        url = reverse('api_editar_usuario', kwargs={'pk': usuario.pk})
        dados = {
            'nome': 'Carlos Silva',
            'email': 'carlosnovo@petlar.com',
            'telefone': '63988888888',
            'tipo_usuario': TIPO_ADOTANTE,
            'status_verificacao_ong': STATUS_ONG_NAO_SE_APLICA,
        }
        response = self.client.put(
            url,
            dados,
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}',
        )

        self.assertEqual(response.status_code, 200)
        usuario.refresh_from_db()
        self.assertEqual(usuario.email, 'carlosnovo@petlar.com')
        self.assertTrue(AuthUser.objects.filter(username='carlosnovo@petlar.com').exists())

    def test_delete_remove_usuario_e_auth_user(self):
        usuario = User.objects.create(
            nome='Carlos',
            email='carlos@petlar.com',
            senha='12345',
            tipo_usuario=TIPO_ADOTANTE,
        )
        AuthUser.objects.create_user(username='carlos@petlar.com', email='carlos@petlar.com', password='12345')
        url = reverse('api_editar_usuario', kwargs={'pk': usuario.pk})
        response = self.client.delete(url, HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.assertEqual(response.status_code, 204)
        self.assertFalse(User.objects.filter(pk=usuario.pk).exists())
        self.assertFalse(AuthUser.objects.filter(username='carlos@petlar.com').exists())


class TestesAPIAutenticacao(TestCase):
    # Classe de testes para autenticação via API

    def setUp(self):
        self.auth_user = AuthUser.objects.create_user(
            username='usuario_teste',
            email='usuario@petlar.com',
            password='12345',
        )
        self.url = reverse('autenticacao_api')

    def test_login_com_email(self):
        response = self.client.post(
            self.url,
            {'username': 'usuario@petlar.com', 'password': '12345'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

    def test_options_com_origem_do_ionic(self):
        response = self.client.options(
            self.url,
            HTTP_ORIGIN='http://127.0.0.1:8100',
            HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Access-Control-Allow-Origin'], '*')

    def test_superuser_retorna_perfil_administrador(self):
        admin = AuthUser.objects.create_superuser(
            username='admin',
            email='admin@petlar.com',
            password='12345',
        )
        User.objects.create(
            nome='Perfil antigo',
            email='admin@petlar.com',
            senha='12345',
            tipo_usuario=TIPO_ADOTANTE,
        )

        response = self.client.post(
            self.url,
            {'username': admin.email, 'password': '12345'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_superuser'])
        self.assertEqual(response.json()['nome_tipo_usuario'], 'Administrador')
