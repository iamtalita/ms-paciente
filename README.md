# Microsserviço de Paciente — PS Saúde Digital

Versão independente para apresentação e teste local, sem modificar o repositório das colegas. Usa Python 3.12, FastAPI, SQLAlchemy assíncrono, PostgreSQL e Docker.

> **Atenção:** esta versão é para demonstração local. As rotas ainda não têm autenticação/autorização e não validam a existência da UBS via `ms-ubs`. Não use dados reais de pacientes. Antes da integração ao sistema real, conectar JWT/roles com `pet_shared`, validar a UBS por API e incluir a rota no gateway.

## Estrutura

- `app/main.py`: inicialização da API e criação das tabelas.
- `app/database.py`: conexão PostgreSQL.
- `app/models/paciente.py`: modelo/tabela de pacientes.
- `app/schemas/paciente.py`: validação dos dados de entrada e saída.
- `app/api/v1/router.py`: endpoints REST.
- `Dockerfile`: imagem do microserviço.
- `docker-compose.yml`: API e banco para demonstração isolada.

## Executar

Na pasta do projeto:

```bash
docker compose up --build
```

- Documentação interativa: http://localhost:8005/docs
- Health check: http://localhost:8005/health
- Parar: `docker compose down`
- Apagar também os dados de demonstração: `docker compose down -v`

## Endpoints

| Método | Rota | Função |
|---|---|---|
| GET | `/health` | Verifica se a API está respondendo |
| POST | `/api/v1/pacientes` | Cadastra paciente |
| GET | `/api/v1/pacientes` | Lista/pesquisa pacientes; aceita `busca`, `ubs_id`, `apenas_ativos`, `limite` |
| GET | `/api/v1/pacientes/{paciente_id}` | Consulta por UUID |
| PATCH | `/api/v1/pacientes/{paciente_id}` | Atualiza dados cadastrais |
| DELETE | `/api/v1/pacientes/{paciente_id}` | Desativa cadastro sem apagar o registro |

{
  "nome": "Maria da Silva",
  "cpf": "529.982.247-25",
  "data_nascimento": "1990-04-15",
  "cns": null,
  "telefone": "89999990000",
  "email": "maria@example.com",
  "endereco": "Rua Exemplo, 100",
  "ubs_id": "00000000-0000-4000-8000-000000000001"
}
```


1. Copiar `app/` para `services/ms-paciente/`.
2. Ajustar o Dockerfile para o padrão do repositório (build context na raiz e instalação de `libs/pet_shared`).
3. Adicionar `db-paciente` e `ms-paciente` ao Compose principal, garantindo que a porta 8005 esteja livre.
4. Adicionar upstream e rota `/api/v1/pacientes` ao `gateway/nginx.conf`.
5. Integrar JWT e perfis com `pet_shared`; validar a UBS via `ms-ubs`.
6. Combinar com a equipe como `ms-agenda` vai referenciar o paciente, sem compartilhar diretamente o banco de dados.
