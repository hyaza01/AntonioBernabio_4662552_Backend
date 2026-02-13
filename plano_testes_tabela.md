# Plano de Testes (Tabela) - Projeto Back End

| ID | Cenário | Endpoint/Método | Pré-condição | Entrada | Esperado (status + pontos) | Evidência (coleção) |
|---|---|---|---|---|---|---|
| T01 | Login ADMIN válido | `POST /auth/login` | Seed aplicado; usuário admin ativo | form-data: username=admin@lanchonete.com, password=admin123 | **200** + `access_token` no response | Auth / T01 - Login ADMIN (positivo) |
| T02 | Cadastro de CLIENTE | `POST /auth/register` | E-mail ainda não cadastrado | JSON com nome, email, senha, consentimento_lgpd | **201** + dados do cliente sem senha/hash | Auth / T02 - Registrar CLIENTE (positivo) |
| T03 | Login CLIENTE válido | `POST /auth/login` | Cliente criado no T02 | form-data: username=cliente.teste@exemplo.com, password=cliente123 | **200** + `access_token`; token salvo em `clienteToken` | Auth / T03 - Login CLIENTE (positivo) |
| T04 | Criar pedido válido com canal | `POST /pedidos` | Cliente autenticado (`clienteToken`); produto/unidade seed | JSON com `unidade_id`, `canalPedido=TOTEM`, itens válidos | **201** + pedido criado; `canal_pedido=TOTEM`; `pedidoId` salvo | Pedidos / T04 - Criar pedido válido (positivo) |
| T05 | Falha sem `canalPedido` | `POST /pedidos` | Cliente autenticado | JSON sem campo `canalPedido` | **422** + erro padronizado de validação | Pedidos / T05 - Criar pedido sem canalPedido (negativo 422) |
| T06 | Falha sem token | `GET /pedidos` | Nenhuma | Sem header Authorization | **401** + erro de autenticação | Pedidos / T06 - Listar pedidos sem token (negativo 401) |
| T07 | Falha por estoque insuficiente | `POST /pedidos` | Cliente autenticado; produto com estoque limitado | JSON com quantidade muito alta (`99999`) | **409** + mensagem de estoque insuficiente | Pedidos / T07 - Criar pedido com estoque insuficiente (negativo 409) |
| T08 | Pagamento mock aprovado | `POST /pagamentos/mock/{pedidoId}` | `pedidoId` criado no T04; ADMIN autenticado (`adminToken`) | JSON `{"aprovado": true, "observacao": "Aprovado no mock"}` | **200** + status do pedido alterado para `PAGO` | Pagamento e Status / T08 - Pagamento mock aprovado (positivo) |
| T09 | Atualizar status para preparo | `PATCH /pedidos/{pedidoId}/status` | Pedido em `PAGO`; ADMIN autenticado | JSON `{"novo_status": "EM_PREPARO"}` | **200** + status atualizado para `EM_PREPARO` | Pagamento e Status / T09 - Atualizar status para EM_PREPARO (positivo) |
| T10 | Falha de autorização por perfil | `POST /unidades` | Cliente autenticado (`clienteToken`) | JSON de criação de unidade | **403** + usuário sem permissão | Autorização / T10 - Cliente tentando criar unidade (negativo 403) |

## Observações para execução
- Ordem recomendada: T01 → T10.
- Tokens e `pedidoId` são preenchidos automaticamente pelos scripts da coleção.
- Evidência prática: resultado de cada request no Postman + status/assertions.
