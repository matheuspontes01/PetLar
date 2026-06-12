import { CapacitorHttp, HttpOptions, HttpResponse } from '@capacitor/core';
import { Component } from '@angular/core';
import { LoadingController, NavController, ToastController } from '@ionic/angular';
import { Storage } from '@ionic/storage-angular';

import { API_BASE_URL } from '../api.config';
import { Usuario } from './usuario.model';

@Component({
  selector: 'app-home',
  standalone: false,
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
  providers: [Storage],
})
export class HomePage {
  public instancia: { username: string; password: string } = {
    username: '',
    password: '',
  };

  public mostrarSenha = false;
  private storageReady?: Promise<Storage>;

  constructor(
    public controleCarregamento: LoadingController,
    public controleToast: ToastController,
    private storage: Storage,
    public controleNavegacao: NavController
  ) {}

  private getStorage(): Promise<Storage> {
    if (!this.storageReady) {
      this.storageReady = this.storage.create();
    }

    return this.storageReady;
  }

  async autenticarUsuario(): Promise<void> {
    if (!this.instancia.username || !this.instancia.password) {
      await this.apresentaMensagem('Informe e-mail/usuario e senha.');
      return;
    }

    const loading = await this.controleCarregamento.create({ message: 'Autenticando...' });
    await loading.present();

    const options: HttpOptions = {
      headers: { 'Content-Type': 'application/json' },
      url: `${API_BASE_URL}/autenticacao-api/`,
      data: this.instancia,
    };

    CapacitorHttp.post(options)
      .then(async (resposta: HttpResponse) => {
        if (resposta.status === 200) {
          const usuario: Usuario = Object.assign(new Usuario(), resposta.data);
          const storage = await this.getStorage();
          await storage.set('usuario', usuario);

          await loading.dismiss();
          this.controleNavegacao.navigateRoot('/pets');
        } else {
          await loading.dismiss();
          await this.apresentaMensagem(`Falha ao autenticar usuario: codigo ${resposta.status}`);
        }
      })
      .catch(async (erro: any) => {
        await loading.dismiss();
        await this.apresentaMensagem(`Falha ao autenticar usuario: codigo ${erro?.status || 'desconhecido'}`);
      });
  }

  public alternarSenha(): void {
    this.mostrarSenha = !this.mostrarSenha;
  }

  private async apresentaMensagem(mensagem: string): Promise<void> {
    const toast = await this.controleToast.create({
      message: mensagem,
      cssClass: 'ion-text-center',
      duration: 2200,
      position: 'bottom',
      color: 'dark',
    });

    await toast.present();
  }
}
