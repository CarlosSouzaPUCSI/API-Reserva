## API Endpoints

[Liste os principais endpoints da API, incluindo as operações disponíveis, os parâmetros esperados e as respostas retornadas.]

### API Reserva - Carlos
#### Endpoint 1
- Método: POST
- URL: /api/reserva
- Parâmetros:
  - Nenhum parâmetro
- Corpo da requisição:
  ```
  {
    "id_cliente": 1,
    "id_sala": 2,
    "entrada": "2026-04-12T11:00:00",
    "saida": "2026-04-12T16:00:00"
  }
  ```
- Resposta:
  - Sucesso (201 CREATED)
    ```
    {
      "id_reserva": 8,
      "id_cliente": 1,
      "id_sala": 2,
      "status": "Confirmada",
      "feito_em": "2026-04-11",
      "entrada": "2026-04-12T11:00:00-03:00",
      "saida": "2026-04-12T16:00:00-03:00"
    }
    ```
  - Erro (400 BAD REQUEST)
    ```
    {
      "detail": "Mensagem de erro depende do tipo de falha teve nos dados de entrada. Exemplo: A entrada fornecida é igual ou após a saída."
    }
    ```
  - Erro (404 NOT FOUND)
    ```
    {
      "detail": "Mensagem de erro depende do tipo de dado que não foi encontrado. Exemplo: O id 1 de cliente enviado não existe."
    }
    ```
  - Erro (409 CONFLICT)
    ```
    {
      "detail": "A sala já está ocupada neste horário"
    }
    ```
#### Endpoint 2
- Método: GET
- URL: /api/reserva
- Parâmetros:
  - id_cliente: int, null
  - id_sala: int, null
  - inicio: date, null
  - fim: date, null
  - offset: int, default = 0
  - limit: int, default = 10, máximo = 100
- Corpo da requisição:
  - Nenhum corpo
- Resposta:
  - Sucesso (200 OK)
    ```
    [
      {
        "id_reserva": 0,
        "id_cliente": 0,
        "id_sala": 0,
        "status": "Confirmada",
        "feito_em": "2026-04-11",
        "entrada": "2026-04-12T11:00:00-03:00",
        "saida": "2026-04-12T16:00:00-03:00"
      }
    ]
    ```
  - Erro (400 BAD REQUEST)
    ```
    {
      "detail": "Se fornecer inicio ou fim, deve fornecer o outro."
    }
    ```
#### Endpoint 3
- Método: GET
- URL: /api/reserva/{id}
- Parâmetros:
  - id: int
- Corpo da requisição:
  - Nenhum corpo
- Resposta:
  - Sucesso (200 OK)
    ```
    {
      "id_reserva": 0,
      "id_cliente": 0,
      "id_sala": 0,
      "status": "Confirmada",
      "feito_em": "2026-04-11",
      "entrada": "2026-04-12T11:00:00-03:00",
      "saida": "2026-04-12T16:00:00-03:00"
    }
    ```
  - Erro (404 NOT FOUND)
    ```
    {
      "detail": "O id 'X' de reservas enviado não existe."
    }
    ```
#### Endpoint 4
- Método: PATCH
- URL: /api/reserva/{id}
- Parâmetros:
  - id: int
- Corpo da requisição:
  ```
  {
    "id_cliente": 0,
    "id_sala": 0,
    "status": "Finalizada",
    "entrada": "2026-04-12T11:00:00",
    "saida": "2026-04-12T16:00:00"
  }
  ```
- Resposta:
  - Sucesso (200 OK)
    ```
    {
      "id_reserva": 0,
      "id_cliente": 0,
      "id_sala": 0,
      "status": "Confirmada",
      "feito_em": "2026-04-11",
      "entrada": "2026-04-12T11:00:00-03:00",
      "saida": "2026-04-12T16:00:00-03:00"
    }
    ```
  - Erro (400 BAD REQUEST)
    ```
    {
      "detail": "Mensagem de erro depende do tipo de falha teve nos dados de entrada. Exemplo: A entrada fornecida é igual ou após a saída."
    }
    ```
  - Erro (404 NOT FOUND)
    ```
    {
      "detail": "Mensagem de erro depende do tipo de dado que não foi encontrado. Exemplo: O id 1 de cliente enviado não existe."
    }
    ```
  - Erro (409 CONFLICT)
    ```
    {
      "detail": "A sala já está ocupada neste horário"
    }
    ```
#### Endpoint 5
- Método: DELETE
- URL: /api/reserva/{id}
- Parâmetros:
  - id: int
- Corpo da requisição:
  - Nenhum corpo
- Resposta:
  - Sucesso (204 NO CONTENT)
  - Erro (404 NOT FOUND)
    ```
    {
      "detail": "O id 'X' de reservas enviado não existe."
    }
    ```

## Implantação

[Instruções para implantar a aplicação distribuída em um ambiente de produção.]

1. Defina os requisitos de hardware e software necessários para implantar a aplicação em um ambiente de produção.
2. Escolha uma plataforma de hospedagem adequada, como um provedor de nuvem ou um servidor dedicado.
3. Configure o ambiente de implantação, incluindo a instalação de dependências e configuração de variáveis de ambiente.
4. Faça o deploy da aplicação no ambiente escolhido, seguindo as instruções específicas da plataforma de hospedagem.
5. Realize testes para garantir que a aplicação esteja funcionando corretamente no ambiente de produção.

## Testes
### API Reserva - Carlos

&nbsp; &nbsp; &nbsp; A estratégia de testes adotada para essa API consistiu na validação de cada rota de forma manual a fim de testar todas as possibilidades de respostas previstas nos endpoints.

&nbsp; &nbsp; &nbsp; As ferramentas utilizadas para atingir este objetivo foram o SwaggerUI e o pgAdmin 4.

#### Teste Endpoint 1 - Criar reserva
- Resultado Esperado:
  - Sucesso (201 CREATED)
  
  &nbsp; &nbsp; &nbsp; Executei a rota com o corpo a seguir:
  ```
  {
    "id_cliente": 1,
    "id_sala": 2,
    "entrada": "2026-04-12T11:00:00",
    "saida": "2026-04-12T16:00:00"
  }
  ```
  &nbsp; &nbsp; &nbsp; Saída recebida pela interface:

  <img width="500" height="500" alt="Teste 1 Imagem 1" src="/img/CarlosTE1I1.png" />

  &nbsp; &nbsp; &nbsp; Confirmação com o pgAdmin:

  <img width="500" height="500" alt="Teste 1 Imagem 2" src="/img/CarlosTE1I2.png" />

  - Erro (400 BAD REQUEST)

  - Erro (404 NOT FOUND)

  - Erro (409 CONFLICT)

#### Teste Endpoint 2 - Listar reservas
#### Teste Endpoint 3 - Listar reservas por ID
#### Teste Endpoint 4 - Editar reservas por ID
#### Teste Endpoint 5 - Deletar reservas por ID