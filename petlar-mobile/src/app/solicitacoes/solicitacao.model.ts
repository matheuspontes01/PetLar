export class Solicitacao {
  public id: number;
  public nome_adotante: string;
  public telefone_adotante: string | null;
  public nome_pet: string;
  public status: string;
  public nome_status: string;
  public mensagem: string;
  public data_solicitacao: string;

  constructor() {
    this.id = 0;
    this.nome_adotante = '';
    this.telefone_adotante = null;
    this.nome_pet = '';
    this.status = '';
    this.nome_status = '';
    this.mensagem = '';
    this.data_solicitacao = '';
  }
}
