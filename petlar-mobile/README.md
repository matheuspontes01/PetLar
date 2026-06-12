# PetLar Mobile

Aplicacao Ionic Angular criada para consumir as APIs do projeto web PetLar.

## Como executar

Instale as dependencias:

```bash
npm install
```

Execute o app:

```bash
npm start
```

O backend Django precisa estar ativo em `http://127.0.0.1:8000`.

## Telas

- Login: autentica em `/autenticacao-api/`.
- Pets para adotante: lista pets disponiveis em `/pets/api/listar/` e permite solicitar adocao.
- Pets para ONG: lista, cria, edita e exclui pets em `/pets/api/gerenciar/`.
- Solicitacoes para adotante: lista e cancela solicitacoes pendentes.
- Solicitacoes para ONG: lista, aprova e rejeita solicitacoes dos pets da ONG.

O token retornado no login e salvo no Ionic Storage e enviado no header `Authorization`.
