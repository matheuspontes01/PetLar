import { CapacitorHttp, HttpOptions, HttpResponse } from '@capacitor/core';
import { Component, OnInit } from '@angular/core';
import { AlertController, LoadingController, NavController, ToastController } from '@ionic/angular';
import { Storage } from '@ionic/storage-angular';

import { API_BASE_URL } from '../api.config';
import { Usuario } from '../home/usuario.model';
import { Solicitacao } from './solicitacao.model';

@Component({
  selector: 'app-solicitacoes',
  standalone: false,
  templateUrl: './solicitacoes.page.html',
  styleUrls: ['./solicitacoes.page.scss'],
  providers: [Storage],
})
export class SolicitacoesPage implements OnInit {
  public usuario: Usuario = new Usuario();
  public solicitacoes: Solicitacao[] = [];
  public carregandoLista = false;
  public mensagemErro = '';

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
      await this.consultarSolicitacoesSistemaWeb();
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

  async consultarSolicitacoesSistemaWeb(): Promise<void> {
    this.carregandoLista = true;
    this.mensagemErro = '';

    const loading = await this.controleCarregamento.create({
      message: 'Pesquisando solicitacoes...',
      spinner: 'crescent',
    });

    await loading.present();

    const options: HttpOptions = {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Token ${this.usuario.token}`,
      },
      url: `${API_BASE_URL}/solicitacoes/api/listar/`,
    };

    CapacitorHttp.get(options)
      .then(async (resposta: HttpResponse) => {
        if (resposta.status === 200 && Array.isArray(resposta.data)) {
          this.solicitacoes = resposta.data.map((solicitacao: any) => Object.assign(new Solicitacao(), solicitacao));
        } else {
          this.solicitacoes = [];
          this.mensagemErro = 'Nao foi possivel carregar as solicitacoes.';
          await this.exibirToast(this.mensagemErro);
        }

        await loading.dismiss();
        this.carregandoLista = false;
      })
      .catch(async (error) => {
        await loading.dismiss();
        this.carregandoLista = false;
        this.solicitacoes = [];
        this.mensagemErro = 'Erro ao consultar solicitacoes. Verifique o backend.';
        await this.exibirToast(this.mensagemErro);
        console.error('Erro ao consultar solicitacoes:', error);
      });
  }

  async voltarPets(): Promise<void> {
    this.controleNavegacao.navigateBack('/pets');
  }

  async abrirUsuarios(): Promise<void> {
    this.controleNavegacao.navigateForward('/usuarios');
  }

  public tituloPainel(): string {
    if (this.podeAvaliar()) {
      return 'Lista de solicitações recebidas';
    }

    return 'Minhas solicitações de adoção';
  }

  public descricaoPainel(): string {
    if (this.podeAvaliar()) {
      return 'Acompanhe, aprove ou rejeite os pedidos enviados para os pets da ONG.';
    }

    return 'Veja o andamento dos pedidos que você enviou para adoção.';
  }

  public ehAdotante(): boolean {
    return this.usuario.tipo_usuario === 'ADOTANTE';
  }

  public podeAvaliar(): boolean {
    return this.usuario.is_superuser || this.usuario.tipo_usuario === 'ONG';
  }

  public ehAdmin(): boolean {
    return this.usuario.is_superuser;
  }

  async cancelarSolicitacao(solicitacao: Solicitacao): Promise<void> {
    const alerta = await this.controleAlerta.create({
      header: 'Cancelar solicitação',
      message: `Deseja cancelar a solicitação para ${solicitacao.nome_pet}?`,
      buttons: [
        { text: 'Voltar', role: 'cancel' },
        {
          text: 'Cancelar',
          role: 'destructive',
          handler: () => {
            this.excluirSolicitacao(solicitacao);
          },
        },
      ],
    });

    await alerta.present();
  }

  async excluirSolicitacaoAdmin(solicitacao: Solicitacao): Promise<void> {
    const alerta = await this.controleAlerta.create({
      header: 'Excluir solicitação',
      message: `Deseja excluir a solicitação para ${solicitacao.nome_pet}?`,
      buttons: [
        { text: 'Voltar', role: 'cancel' },
        {
          text: 'Excluir',
          role: 'destructive',
          handler: () => {
            this.excluirSolicitacao(solicitacao);
          },
        },
      ],
    });

    await alerta.present();
  }

  async excluirSolicitacao(solicitacao: Solicitacao): Promise<void> {
    const options: HttpOptions = {
      headers: {
        Authorization: `Token ${this.usuario.token}`,
      },
      url: `${API_BASE_URL}/solicitacoes/api/editar/${solicitacao.id}/`,
    };

    CapacitorHttp.delete(options)
      .then(async (resposta: HttpResponse) => {
        if (resposta.status === 204) {
          await this.exibirToast('Solicitação cancelada.');
          await this.consultarSolicitacoesSistemaWeb();
        } else {
          await this.exibirToast(`Falha ao cancelar: codigo ${resposta.status}`);
        }
      })
      .catch(async () => {
        await this.exibirToast('Erro ao cancelar solicitação.');
      });
  }

  async avaliarSolicitacao(solicitacao: Solicitacao, status: string): Promise<void> {
    const options: HttpOptions = {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Token ${this.usuario.token}`,
      },
      url: `${API_BASE_URL}/solicitacoes/api/editar/${solicitacao.id}/`,
      data: { status },
    };

    CapacitorHttp.patch(options)
      .then(async (resposta: HttpResponse) => {
        if (resposta.status === 200) {
          await this.exibirToast('Solicitação atualizada.');
          await this.consultarSolicitacoesSistemaWeb();
        } else {
          await this.exibirToast(`Falha ao avaliar: codigo ${resposta.status}`);
        }
      })
      .catch(async () => {
        await this.exibirToast('Erro ao avaliar solicitação.');
      });
  }

  async atualizarLista(event?: CustomEvent): Promise<void> {
    await this.consultarSolicitacoesSistemaWeb();

    if (event?.target && 'complete' in event.target) {
      (event.target as HTMLIonRefresherElement).complete();
    }
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
