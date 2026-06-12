export class Pet {
  public id: number;
  public nome: string;
  public especie: string;
  public raca: string;
  public fotos?: string;
  public idade: number;
  public idade_texto: string;
  public sexo: string;
  public nome_sexo: string;
  public porte: string;
  public nome_porte: string;
  public vacinado: boolean;
  public castrado: boolean;
  public descricao: string;
  public status: string;
  public nome_status: string;
  public responsavel?: number;
  public nome_responsavel: string | null;

  constructor() {
    this.id = 0;
    this.nome = '';
    this.especie = '';
    this.raca = '';
    this.idade = 0;
    this.idade_texto = '';
    this.sexo = '';
    this.nome_sexo = '';
    this.porte = '';
    this.nome_porte = '';
    this.vacinado = false;
    this.castrado = false;
    this.descricao = '';
    this.status = '';
    this.nome_status = '';
    this.nome_responsavel = null;
  }
}
