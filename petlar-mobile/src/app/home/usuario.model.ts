export class Usuario {
  public id: number;
  public nome: string;
  public email: string;
  public token: string;
  public tipo_usuario: string;
  public nome_tipo_usuario: string;
  public ong_aprovada: boolean;
  public is_superuser: boolean;

  constructor() {
    this.id = 0;
    this.nome = '';
    this.email = '';
    this.token = '';
    this.tipo_usuario = '';
    this.nome_tipo_usuario = '';
    this.ong_aprovada = false;
    this.is_superuser = false;
  }
}
