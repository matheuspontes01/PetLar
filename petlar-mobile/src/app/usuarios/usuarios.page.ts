import { CapacitorHttp, HttpOptions, HttpResponse } from '@capacitor/core';
import { Component, OnInit } from '@angular/core';
import { AlertController, LoadingController, NavController, ToastController } from '@ionic/angular';
import { Storage } from '@ionic/storage-angular';

import { API_BASE_URL } from '../api.config';
import { Usuario } from '../home/usuario.model';
import { UsuarioSistema } from './usuario-sistema.model';

@Component({
  selector: 'app-usuarios',
  standalone: false,
  templateUrl: './usuarios.page.html',
  styleUrls: ['./usuarios.page.scss'],
  providers: [Storage],
})
export class UsuariosPage implements OnInit {
  public usuario: Usuario = new Usuario();
  public usuarios: UsuarioSistema[] = [];
  public usuarioFormulario: UsuarioSistema = new UsuarioSistema();
  public pesquisa = '';
  public carregandoLista = false;
  public mostrarFormulario = false;

  private storageReady?: Promise<Storage>;

  constructor(
    private storage: Storage,
    private controleAlerta: AlertController,
    private controleCarregamento: LoadingController,
    private controleToast: ToastController,
    private controleNavegacao: NavController,
  ) {}

  async ngOnInit(): Promise<void> {
    const storage = await this.getStorage();
    const registro = await storage.get('usuario');

    if (registro) {
      this.usuario = Object.assign(new Usuario(), registro);
      if (!this.usuario.is_superuser) {
        this.controleNavegacao.navigateRoot('/pets');
        return;
      }
      await this.consultarUsuariosSistemaWeb();
    } else {
      this.controleNavegacao.navigateRoot('/home');
    }
  }

  private getStorage(): Promise<Storage> {
    if (!this.storageReady) {
      this.storageReady = this.storage.create();
    }

    return this.storageReady;
  }

  async consultarUsuariosSistemaWeb(): Promise<void> {
    this.carregandoLista = true;

    const loading = await this.controleCarregamento.create({
      message: 'Pesquisando usuarios...',
      spinner: 'crescent',
    });
    await loading.present();

    const params = this.pesquisa ? `?pesquisa=${encodeURIComponent(this.pesquisa)}` : '';
    const options: HttpOptions = {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Token ${this.usuario.token}`,
      },
      url: `${API_BASE_URL}/usuarios/api/gerenciar/${params}`,
    };

    CapacitorHttp.get(options)
      .then(async (resposta: HttpResponse) => {
        if (resposta.status === 200 && Array.isArray(resposta.data)) {
          this.usuarios = resposta.data.map((item: any) => Object.assign(new UsuarioSistema(), item));
        } else {
          this.usuarios = [];
          await this.exibirToast(`Falha ao carregar usuarios: codigo ${resposta.status}`);
        }

        await loading.dismiss();
        this.carregandoLista = false;
      })
      .catch(async () => {
        await loading.dismiss();
        this.carregandoLista = false;
        this.usuarios = [];
        await this.exibirToast('Erro ao consultar usuarios.');
      });
  }

  public novoUsuario(): void {
    this.usuarioFormulario = new UsuarioSistema();
    this.mostrarFormulario = true;
  }

  public editarUsuario(usuario: UsuarioSistema): void {
    this.usuarioFormulario = Object.assign(new UsuarioSistema(), usuario);
    this.usuarioFormulario.senha = '';
    this.mostrarFormulario = true;
  }

  public cancelarFormulario(): void {
    this.usuarioFormulario = new UsuarioSistema();
    this.mostrarFormulario = false;
  }

  public get ongsPendentes(): UsuarioSistema[] {
    return this.usuarios.filter((item) => {
      return item.tipo_usuario === 'ONG' && item.status_verificacao_ong === 'PENDENTE';
    });
  }

  async salvarUsuario(): Promise<void> {
    if (!this.usuarioFormulario.nome || !this.usuarioFormulario.email || !this.usuarioFormulario.tipo_usuario) {
      await this.exibirToast('Preencha nome, e-mail e tipo.');
      return;
    }

    if (!this.usuarioFormulario.id && !this.usuarioFormulario.senha) {
      await this.exibirToast('Informe uma senha para novo usuario.');
      return;
    }

    if (this.usuarioFormulario.tipo_usuario !== 'ONG') {
      this.usuarioFormulario.status_verificacao_ong = 'NAO_SE_APLICA';
    }

    const editando = this.usuarioFormulario.id > 0;
    const options: HttpOptions = {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Token ${this.usuario.token}`,
      },
      url: editando
        ? `${API_BASE_URL}/usuarios/api/gerenciar/${this.usuarioFormulario.id}/`
        : `${API_BASE_URL}/usuarios/api/gerenciar/`,
      data: this.dadosFormulario(),
    };

    const requisicao = editando ? CapacitorHttp.put(options) : CapacitorHttp.post(options);
    requisicao
      .then(async (resposta: HttpResponse) => {
        if (resposta.status === 200 || resposta.status === 201) {
          await this.exibirToast('Usuario salvo com sucesso.');
          this.cancelarFormulario();
          await this.consultarUsuariosSistemaWeb();
        } else {
          await this.exibirToast(`Falha ao salvar usuario: codigo ${resposta.status}`);
        }
      })
      .catch(async () => {
        await this.exibirToast('Erro ao salvar usuario.');
      });
  }

  private dadosFormulario(): any {
    const dados: any = {
      nome: this.usuarioFormulario.nome,
      email: this.usuarioFormulario.email,
      telefone: this.usuarioFormulario.telefone,
      tipo_usuario: this.usuarioFormulario.tipo_usuario,
      razao_social_ong: this.usuarioFormulario.razao_social_ong,
      cnpj_ong: this.usuarioFormulario.cnpj_ong,
      status_verificacao_ong: this.usuarioFormulario.status_verificacao_ong,
    };

    if (this.usuarioFormulario.senha) {
      dados.senha = this.usuarioFormulario.senha;
    }

    return dados;
  }

  async avaliarOng(usuario: UsuarioSistema, status: string): Promise<void> {
    const dados = Object.assign(new UsuarioSistema(), usuario);
    dados.status_verificacao_ong = status;
    dados.senha = '';
    this.usuarioFormulario = dados;
    await this.salvarUsuario();
  }

  async excluirUsuario(usuario: UsuarioSistema): Promise<void> {
    const alerta = await this.controleAlerta.create({
      header: 'Excluir usuário',
      message: `Deseja excluir ${usuario.nome}?`,
      buttons: [
        { text: 'Cancelar', role: 'cancel' },
        {
          text: 'Excluir',
          role: 'destructive',
          handler: () => {
            this.confirmarExclusaoUsuario(usuario);
          },
        },
      ],
    });

    await alerta.present();
  }

  async confirmarExclusaoUsuario(usuario: UsuarioSistema): Promise<void> {
    const options: HttpOptions = {
      headers: {
        Authorization: `Token ${this.usuario.token}`,
      },
      url: `${API_BASE_URL}/usuarios/api/gerenciar/${usuario.id}/`,
    };

    CapacitorHttp.delete(options)
      .then(async (resposta: HttpResponse) => {
        if (resposta.status === 204) {
          await this.exibirToast('Usuario excluido com sucesso.');
          await this.consultarUsuariosSistemaWeb();
        } else {
          await this.exibirToast(`Falha ao excluir usuario: codigo ${resposta.status}`);
        }
      })
      .catch(async () => {
        await this.exibirToast('Erro ao excluir usuario.');
      });
  }

  async abrirPets(): Promise<void> {
    this.controleNavegacao.navigateRoot('/pets');
  }

  async abrirSolicitacoes(): Promise<void> {
    this.controleNavegacao.navigateForward('/solicitacoes');
  }

  async sair(): Promise<void> {
    const storage = await this.getStorage();
    await storage.remove('usuario');
    this.controleNavegacao.navigateRoot('/home');
  }

  private async exibirToast(mensagem: string): Promise<void> {
    const toast = await this.controleToast.create({
      message: mensagem,
      duration: 2000,
      position: 'bottom',
      color: 'dark',
    });

    await toast.present();
  }
}
