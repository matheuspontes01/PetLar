import { CapacitorHttp, HttpOptions, HttpResponse } from '@capacitor/core';
import { Component, OnInit } from '@angular/core';
import { AlertController, LoadingController, NavController, ToastController } from '@ionic/angular';
import { Storage } from '@ionic/storage-angular';

import { API_BASE_URL } from '../api.config';
import { Usuario } from '../home/usuario.model';
import { Pet } from './pet.model';

@Component({
  selector: 'app-pets',
  standalone: false,
  templateUrl: './pets.page.html',
  styleUrls: ['./pets.page.scss'],
  providers: [Storage],
})
export class PetsPage implements OnInit {
  public usuario: Usuario = new Usuario();
  public pets: Pet[] = [];
  public carregandoLista = false;
  public mensagemErro = '';
  public pesquisa = '';
  public mostrarFormulario = false;
  public petFormulario: Pet = new Pet();
  public ongsPendentesCount = 0;
  public solicitacoesPendentesCount = 0;

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
      await this.consultarPetsSistemaWeb();
      await this.consultarAvisosSistemaWeb();
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

  async consultarPetsSistemaWeb(): Promise<void> {
    this.carregandoLista = true;
    this.mensagemErro = '';

    const loading = await this.controleCarregamento.create({
      message: 'Pesquisando pets...',
      spinner: 'crescent',
    });

    await loading.present();

    const params = this.pesquisa ? `?pesquisa=${encodeURIComponent(this.pesquisa)}` : '';
    const rota = this.podeGerenciarPets() ? '/pets/api/gerenciar/' : '/pets/api/listar/';
    const options: HttpOptions = {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Token ${this.usuario.token}`,
      },
      url: `${API_BASE_URL}${rota}${params}`,
    };

    CapacitorHttp.get(options)
      .then(async (resposta: HttpResponse) => {
        if (resposta.status === 200 && Array.isArray(resposta.data)) {
          this.pets = resposta.data.map((pet: any) => Object.assign(new Pet(), pet));
        } else {
          this.pets = [];
          this.mensagemErro = 'Nao foi possivel carregar os pets disponiveis.';
          await this.exibirToast(this.mensagemErro);
        }

        await loading.dismiss();
        this.carregandoLista = false;
      })
      .catch(async (error) => {
        await loading.dismiss();
        this.carregandoLista = false;
        this.pets = [];
        this.mensagemErro = 'Erro ao consultar pets. Verifique o backend.';
        await this.exibirToast(this.mensagemErro);
        console.error('Erro ao consultar pets:', error);
      });
  }

  obterFoto(url?: string): string {
    if (!url) {
      return 'assets/icon/favicon.png';
    }

    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }

    return `${API_BASE_URL}${url.startsWith('/') ? '' : '/'}${url}`;
  }

  async atualizarLista(event?: CustomEvent): Promise<void> {
    await this.consultarPetsSistemaWeb();
    await this.consultarAvisosSistemaWeb();

    if (event?.target && 'complete' in event.target) {
      (event.target as HTMLIonRefresherElement).complete();
    }
  }

  async abrirSolicitacoes(): Promise<void> {
    this.controleNavegacao.navigateForward('/solicitacoes');
  }

  async abrirUsuarios(): Promise<void> {
    this.controleNavegacao.navigateForward('/usuarios');
  }

  async consultarAvisosSistemaWeb(): Promise<void> {
    if (this.ehAdmin()) {
      await this.consultarOngsPendentesSistemaWeb();
    }

    if (this.usuario.tipo_usuario === 'ONG' && this.usuario.ong_aprovada) {
      await this.consultarSolicitacoesPendentesSistemaWeb();
    }
  }

  async consultarOngsPendentesSistemaWeb(): Promise<void> {
    const options: HttpOptions = {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Token ${this.usuario.token}`,
      },
      url: `${API_BASE_URL}/usuarios/api/gerenciar/`,
    };

    CapacitorHttp.get(options)
      .then((resposta: HttpResponse) => {
        if (resposta.status === 200 && Array.isArray(resposta.data)) {
          this.ongsPendentesCount = resposta.data.filter((item: any) => {
            return item.tipo_usuario === 'ONG' && item.status_verificacao_ong === 'PENDENTE';
          }).length;
        }
      })
      .catch(() => {
        this.ongsPendentesCount = 0;
      });
  }

  async consultarSolicitacoesPendentesSistemaWeb(): Promise<void> {
    const options: HttpOptions = {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Token ${this.usuario.token}`,
      },
      url: `${API_BASE_URL}/solicitacoes/api/listar/`,
    };

    CapacitorHttp.get(options)
      .then((resposta: HttpResponse) => {
        if (resposta.status === 200 && Array.isArray(resposta.data)) {
          this.solicitacoesPendentesCount = resposta.data.filter((item: any) => {
            return item.status === 'PENDENTE';
          }).length;
        }
      })
      .catch(() => {
        this.solicitacoesPendentesCount = 0;
      });
  }

  public ehAdmin(): boolean {
    return this.usuario.is_superuser;
  }

  public tituloPainel(): string {
    if (this.podeGerenciarPets()) {
      return this.ehAdmin() ? 'Lista de todos os pets' : 'Lista de pets da ONG';
    }

    return 'Lista de pets para adoção';
  }

  public descricaoPainel(): string {
    if (this.podeGerenciarPets()) {
      return 'Cadastre, edite e acompanhe os pets disponíveis no PetLar.';
    }

    return 'Escolha um pet disponível e envie sua solicitação de adoção.';
  }

  public ehAdotante(): boolean {
    return this.usuario.tipo_usuario === 'ADOTANTE';
  }

  public podeGerenciarPets(): boolean {
    return this.usuario.is_superuser || (this.usuario.tipo_usuario === 'ONG' && this.usuario.ong_aprovada);
  }

  public novoPet(): void {
    this.petFormulario = new Pet();
    this.petFormulario.sexo = '1';
    this.petFormulario.porte = '1';
    this.petFormulario.status = '1';
    this.mostrarFormulario = true;
  }

  public editarPet(pet: Pet): void {
    this.petFormulario = Object.assign(new Pet(), pet);
    this.mostrarFormulario = true;
  }

  public cancelarFormulario(): void {
    this.mostrarFormulario = false;
    this.petFormulario = new Pet();
  }

  async salvarPet(): Promise<void> {
    if (!this.petFormulario.nome || !this.petFormulario.especie || !this.petFormulario.raca || !this.petFormulario.idade || !this.petFormulario.descricao) {
      await this.exibirToast('Preencha os dados principais do pet.');
      return;
    }

    const editando = this.petFormulario.id > 0;
    const options: HttpOptions = {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Token ${this.usuario.token}`,
      },
      url: editando
        ? `${API_BASE_URL}/pets/api/gerenciar/${this.petFormulario.id}/`
        : `${API_BASE_URL}/pets/api/gerenciar/`,
      data: {
        nome: this.petFormulario.nome,
        especie: this.petFormulario.especie,
        raca: this.petFormulario.raca,
        idade: this.petFormulario.idade,
        sexo: this.petFormulario.sexo,
        porte: this.petFormulario.porte,
        vacinado: this.petFormulario.vacinado,
        castrado: this.petFormulario.castrado,
        descricao: this.petFormulario.descricao,
        status: this.petFormulario.status,
      },
    };

    const requisicao = editando ? CapacitorHttp.put(options) : CapacitorHttp.post(options);
    requisicao
      .then(async (resposta: HttpResponse) => {
        if (resposta.status === 200 || resposta.status === 201) {
          await this.exibirToast('Pet salvo com sucesso.');
          this.cancelarFormulario();
          await this.consultarPetsSistemaWeb();
        } else {
          await this.exibirToast(`Falha ao salvar pet: codigo ${resposta.status}`);
        }
      })
      .catch(async () => {
        await this.exibirToast('Erro ao salvar pet.');
      });
  }

  async excluirPet(pet: Pet): Promise<void> {
    const alerta = await this.controleAlerta.create({
      header: 'Excluir pet',
      message: `Deseja excluir ${pet.nome}?`,
      buttons: [
        { text: 'Cancelar', role: 'cancel' },
        {
          text: 'Excluir',
          role: 'destructive',
          handler: () => {
            this.confirmarExclusaoPet(pet);
          },
        },
      ],
    });

    await alerta.present();
  }

  async confirmarExclusaoPet(pet: Pet): Promise<void> {
    const options: HttpOptions = {
      headers: {
        Authorization: `Token ${this.usuario.token}`,
      },
      url: `${API_BASE_URL}/pets/api/gerenciar/${pet.id}/`,
    };

    CapacitorHttp.delete(options)
      .then(async (resposta: HttpResponse) => {
        if (resposta.status === 204) {
          await this.exibirToast('Pet excluido com sucesso.');
          await this.consultarPetsSistemaWeb();
        } else {
          await this.exibirToast(`Falha ao excluir pet: codigo ${resposta.status}`);
        }
      })
      .catch(async () => {
        await this.exibirToast('Erro ao excluir pet.');
      });
  }

  async solicitarAdocao(pet: Pet): Promise<void> {
    const alerta = await this.controleAlerta.create({
      header: `Solicitar ${pet.nome}`,
      inputs: [
        {
          name: 'mensagem',
          type: 'textarea',
          placeholder: 'Conte brevemente por que deseja adotar.',
        },
      ],
      buttons: [
        { text: 'Cancelar', role: 'cancel' },
        {
          text: 'Enviar',
          handler: (dados) => {
            this.enviarSolicitacao(pet, dados.mensagem || 'Tenho interesse na adoção.');
          },
        },
      ],
    });

    await alerta.present();
  }

  async enviarSolicitacao(pet: Pet, mensagem: string): Promise<void> {
    const options: HttpOptions = {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Token ${this.usuario.token}`,
      },
      url: `${API_BASE_URL}/solicitacoes/api/novo/${pet.id}/`,
      data: { mensagem },
    };

    CapacitorHttp.post(options)
      .then(async (resposta: HttpResponse) => {
        if (resposta.status === 201) {
          await this.exibirToast('Solicitacao enviada com sucesso.');
          this.controleNavegacao.navigateForward('/solicitacoes');
        } else {
          await this.exibirToast(resposta.data?.detail || `Falha ao solicitar: codigo ${resposta.status}`);
        }
      })
      .catch(async (erro) => {
        await this.exibirToast(erro?.data?.detail || 'Erro ao enviar solicitacao.');
      });
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
