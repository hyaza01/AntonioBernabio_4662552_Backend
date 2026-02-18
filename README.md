# Projeto Back End - Lanchonete Multicanal

API REST em FastAPI para atender o roteiro da atividade prática 2026 (trilha Back-End), com autenticação JWT, controle por perfis, fluxo de pedido com pagamento mock, controle de estoque por unidade, fidelidade e documentação Swagger/OpenAPI.

## Requisitos
- Python 3.11+ (testado com Python 3.14)
- pip

## Configuração
1. Crie e ative um ambiente virtual.
2. Instale dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Copie `.env.example` para `.env` e ajuste se necessário.

## Executar API
```bash
uvicorn app.main:app --reload
```

## Como publicar (Render)
1. Suba o projeto no GitHub (repositório público).
2. Acesse Render e crie um novo **Web Service** conectado ao repositório.
3. Configure:
   - Runtime: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Em **Environment Variables**, configure:
   - `APP_NAME=Projeto Back End - Lanchonete`
   - `SECRET_KEY=<uma-chave-forte>`
   - `ACCESS_TOKEN_EXPIRE_MINUTES=120`
   - `DATABASE_URL=sqlite:///./app.db`
5. Faça o deploy e copie a URL pública gerada (ex.: `https://seu-app.onrender.com`).

Observação: com SQLite em hospedagem gratuita, os dados podem ser reiniciados após restart/deploy. Para persistência robusta em nuvem, use banco gerenciado (PostgreSQL).

## Documentação
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Coleção de testes Postman (obrigatória)
- Coleção: `postman/Projeto_BackEnd_UNINTER.postman_collection.json`
- Ambiente: `postman/Projeto_BackEnd_UNINTER.postman_environment.json`

### Ordem sugerida de execução (10 cenários)
1. T01 - Login ADMIN (positivo)
2. T02 - Registrar CLIENTE (positivo)
3. T03 - Login CLIENTE (positivo)
4. T04 - Criar pedido válido (positivo)
5. T05 - Criar pedido sem canalPedido (negativo 422)
6. T06 - Listar pedidos sem token (negativo 401)
7. T07 - Criar pedido com estoque insuficiente (negativo 409)
8. T08 - Pagamento mock aprovado (positivo)
9. T09 - Atualizar status para EM_PREPARO (positivo)
10. T10 - Cliente tentando criar unidade (negativo 403)

Cobertura mínima atendida na coleção:
- Autenticação/autorização (200, 401, 403)
- Validação de dados (422)
- Regra de negócio (estoque insuficiente 409)
- Pagamento mock aprovado com atualização de status

## Como testar (local e publicado)
### Local
1. Inicie a API: `uvicorn app.main:app --reload`
2. Abra o Swagger: `http://127.0.0.1:8000/docs`
3. Teste primeiro `POST /auth/login` com admin seed:
   - `admin@lanchonete.com` / `admin123`
4. Execute o fluxo completo pelo Swagger ou Postman.

### Publicado
1. Troque o `baseUrl` no ambiente Postman para sua URL pública.
2. Execute os cenários na ordem T01 → T10.
3. Valide no Swagger publicado:
   - `https://SUA-URL/docs`
   - `https://SUA-URL/openapi.json`

## Usuário seed
Na primeira execução, é criado automaticamente:
- E-mail: `admin@lanchonete.com`
- Senha: `admin123`
- Perfil: `ADMIN`

Também é criado seed de:
- 1 unidade (`Unidade Centro`)
- 1 produto (`X-Burger`)
- estoque inicial de 100 itens

## Endpoints principais
### Auth
- `POST /auth/register` (cliente)
- `POST /auth/register-interno` (ADMIN)
- `POST /auth/login`
- `GET /auth/me`

### Catálogo e estoque
- `POST /unidades`
- `GET /unidades`
- `POST /produtos`
- `GET /produtos?page=1&limit=10`
- `POST /estoque/movimentacoes`
- `GET /estoque/saldo?unidadeId=1&produtoId=1`

### Pedidos / pagamento
- `POST /pedidos` (campo obrigatório `canalPedido`: APP, TOTEM, BALCAO, PICKUP, WEB)
- `GET /pedidos?canalPedido=TOTEM&status=AGUARDANDO_PAGAMENTO`
- `POST /pagamentos/mock/{pedido_id}`
- `PATCH /pedidos/{pedido_id}/status`

### Fidelidade
- `GET /fidelidade/saldo/{cliente_id}`
- `POST /fidelidade/resgatar/{cliente_id}`

## Regras implementadas
- Autenticação com JWT.
- Autorização por `role` (ADMIN, GERENTE, COZINHA, ATENDENTE, CLIENTE).
- Hash de senha com PBKDF2-SHA256.
- Padrão de erro JSON unificado.
- Criação de pedido exige `canalPedido` e itens.
- Validação de estoque por unidade na criação do pedido.
- Pagamento mock com aprovação/recusa e atualização de status.
- Fidelidade: pontos somados em pagamento aprovado e possibilidade de resgate.
- Auditoria básica em ações sensíveis (criação de pedido, pagamento, mudança de status).

## Fluxo crítico (MVP)
1. Cliente faz login.
2. Cliente cria pedido com `canalPedido`.
3. Sistema valida estoque e grava pedido + itens.
4. Atendente/gerente processa pagamento mock.
5. Pedido muda status para `PAGO` ou `PAGAMENTO_RECUSADO`.
6. Cozinha/gerente/admin atualiza status operacional (`EM_PREPARO`, `PRONTO`, `ENTREGUE`).

## Observações
- Banco utilizado: SQLite (`app.db`) para execução local simples.
- Estrutura organizada em camadas: domínio, aplicação, infraestrutura e API.
