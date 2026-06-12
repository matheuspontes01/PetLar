export class UsuarioSistema {
  public id: number;
  public nome: string;
  public email: string;
  public senha: string;
  public telefone: string;
  public tipo_usuario: string;
  public nome_tipo_usuario: string;
  public razao_social_ong: string;
  public cnpj_ong: string;
  public status_verificacao_ong: string;
  public nome_status_verificacao_ong: string;

  constructor() {
    this.id = 0;
    this.nome = '';
    this.email = '';
    this.senha = '';
    this.telefone = '';
    this.tipo_usuario = 'ADOTANTE';
    this.nome_tipo_usuario = '';
    this.razao_social_ong = '';
    this.cnpj_ong = '';
    this.status_verificacao_ong = 'NAO_SE_APLICA';
    this.nome_status_verificacao_ong = '';
  }
}
