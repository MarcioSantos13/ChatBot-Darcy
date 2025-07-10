# 🤖 Chatbot-Darcy
## Branch API-FASTAPI


Um chatbot inteligente treinável com base de dados própria, integração via Flask e MySQL, fallback com ChatterBot, busca fuzzy e interface para treinamento. Ideal para suporte educacional (ex: Plataforma Aprender da UnB).

---

## 📌 Visão Geral

- **Backend**: Flask + MySQL
- **IA auxiliar**: ChatterBot (fallback)
- **Busca por similaridade**: fuzzywuzzy
- **Treinável via interface**
- **Interface web responsiva**
- **Backup automático com Python**
- **Integração futura com API própria de IA**

---

## 🗂️ Estrutura do Projeto


## Estrutura chatbot_darcy
```
chatbot_darcy/
├── app.py                     # Lógica principal da aplicação
├── templates/
│   ├── index.html             # Chat principal
│   ├── train.html             # Treinamento de perguntas
│   └── list_questions.html    # Listagem das perguntas cadastradas
├── static/css/styles.css      # Estilo visual do chatbot
├── backups/                   # Pasta de backups .sql
├── backup_mysql.py            # Script para backup do banco MySQL
├── chatbot_darcy.sql          # Dump manual do banco
├── requirements.txt           # Dependências do projeto
└── database.sqlite3           # Banco local do ChatterBot (fallback)
```

---

## 🧠 Fluxo de Resposta do Chat

1. Usuário envia mensagem via interface (`/get`)
2. A pergunta é **normalizada** (minúscula, sem pontuação)
3. Compara com o banco de perguntas/respostas via `fuzzywuzzy`
   - Usa média de `token_set_ratio` e `partial_ratio`
   - Score mínimo para validação: **75**
4. Se encontrar correspondência → retorna a resposta
5. Senão:
   - Se for uma **saudação simples**, responde com cumprimento
   - Senão, utiliza o **ChatterBot (fallback)**
   - Se confiança < 0.5 → resposta padrão + orientação de suporte
6. Resposta é salva no MySQL via `salvar_interacao()`

---

## 🔧 Funções Importantes

### `normalizar_texto(texto)`
> Remove pontuação e transforma a entrada em minúsculas para facilitar a busca.

### `salvar_interacao(pergunta, resposta)`
> Insere ou atualiza uma interação no banco MySQL, usando a versão normalizada da pergunta.

### `get_response()`
> Função principal que comanda o fluxo: fuzzy → saudação → fallback → salva.

### `backup_mysql.py`
> Script externo que cria um backup `.sql` do banco MySQL automaticamente.

---

## 📃 Regras de Similaridade

| Técnica              | O que faz                                          |
|----------------------|----------------------------------------------------|
| `token_set_ratio`    | Ignora ordem, foca nas palavras                     |
| `partial_ratio`      | Permite partes semelhantes                         |
| Média combinada ≥ 75 | Considerada como match válido                      |

---

## 💡 Detecção de Saudação

Responde com “Olá! Como posso te ajudar?” se a frase do usuário for **exatamente**:

```
"bom dia", "boa tarde", "boa noite", "oi", "olá", "ola"
```

---

## 🧪 Log no Terminal

Ao responder, Darcy informa qual mecanismo foi utilizado:

```
📌 [Fuzzy] Pergunta: "como acesso o curso?" | Score: 91.0
👋 [Saudação] Pergunta: "oi"
🧠 [Fallback] Pergunta: "xytzq" | Resposta: "Desculpe, não entendi sua pergunta."
```

---

## 🛠️ Dependências

Instale com:

```bash
pip install -r requirements.txt
```

Incluem:
- Flask
- mysql-connector-python
- fuzzywuzzy
- python-dotenv (para futura integração com APIs externas)
- chatterbot
- unidecode (opcional)

---

## 🚀 Futuras Expansões

- [ ] Integração com API externa de IA
- [ ] Painel de métricas (interações, perguntas mais comuns)
- [ ] Controle de histórico via localStorage
- [ ] Interface multilíngue
- [ ] Upload em lote de CSV para treinamento em massa

---

## 👨‍💻 Desenvolvido por

**Márcio F. Santos**  
Com apoio técnico do assistente Copilot da Microsoft 😄

---
