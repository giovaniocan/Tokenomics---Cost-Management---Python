# Otimização de Contexto para LLMs

[English](README.md) · **Português**

> Comparação prática de estratégias de gerenciamento de tokens para aplicações baseadas em LLMs usando Google Gemini e Python.

![Painel de otimização de contexto LLM mostrando economia de tokens entre três estratégias](docs/screenshots/dashboard.png)

## Sobre

Gerenciar a janela de contexto é crítico tanto para eficiência de custo quanto para qualidade de resposta em aplicações com LLMs. Este projeto demonstra e compara três abordagens para lidar com restrições de tokens numa conversa sintética de atendimento com 50 mensagens, comparando a contagem offline de tokens (tiktoken) com a contagem real da API do Google Gemini.

## Funcionalidades

- **Comparação baseline** — envio da conversa inteira em cada requisição
- **Context pruning** — remove as mensagens mais antigas até caber no orçamento de tokens
- **Summarization buffer** — resume mensagens antigas via API, mantém as recentes
- **Contagem offline vs. online** — compara aproximação do tiktoken contra contagens reais da API
- **Contagem real pela API** — cada estratégia é medida com a API `count_tokens` do Gemini, sem estimativa
- **Métricas detalhadas** — mostra contagem de mensagens preservadas, economia de tokens e detalhamento de custo por estratégia

## Exemplo de saída

O painel exibe contagens de tokens para cada estratégia e mostra economia quando aplicada à mesma conversa:

```
════════════════════════════════════════════════════════════
🚀 LLM CONTEXT OPTIMIZATION DASHBOARD (50 MESSAGES)
════════════════════════════════════════════════════════════

1️⃣ BASELINE: FULL HISTORY SUBMISSION
   ├─ Expectation (Offline - Tiktoken): 1200 tokens
   └─ Real Cost (Online API):           1042 tokens

2️⃣ STRATEGY A: CONTEXT PRUNING
   ├─ Preserved messages: 8 out of 50
   └─ New call cost:      149 tokens

3️⃣ STRATEGY B: SUMMARIZATION BUFFER (SUMMARIZER AGENT)
   ├─ Structure:          1 Summary + 4 Recent Messages
   ├─ New call cost:      126 tokens
   └─ 💰 TOTAL SAVINGS:   916 tokens saved per request!

════════════════════════════════════════════════════════════
```

## Tecnologias

- **Linguagem:** Python 3.11+
- **LLM:** Google Gemini API (`gemini-2.5-flash-lite`)
- **Contagem de tokens:** tiktoken (tokenizador do OpenAI para referência offline)
- **Configuração:** python-dotenv

## Como rodar

### Pré-requisitos

- Python 3.11 ou superior
- Uma chave da API do Google Gemini ([Google AI Studio](https://aistudio.google.com/apikey))

### Instalação

```bash
git clone https://github.com/giovaniocan/Tokenomics---Cost-Management---Python.git
cd Tokenomics---Cost-Management---Python
pip install google-genai tiktoken python-dotenv
```

### Configuração

Crie um arquivo `.env` na raiz do projeto com sua chave da API do Gemini:

```bash
echo "GEMINI_API_KEY=sua_chave_aqui" > .env
```

### Execução

```bash
python exercicio1.py
```

## Variáveis de ambiente

| Variável | Para quê |
| --- | --- |
| `GEMINI_API_KEY` | Sua chave da API do Google Gemini |

## Principais aprendizados

- **Tiktoken ≠ tokenizador do Gemini** — contagem offline via tiktoken é uma aproximação; contagens reais da API podem diferir
- **Pruning é simples mas remove contexto** — estratégia agressiva descarta as mensagens mais antigas para caber no orçamento
- **Summarization retém mais contexto** — combina um resumo de mensagens antigas com as recentes, como mostrado no painel
- **Economia mensurável** — o painel demonstra redução de tokens entre estratégias, com a abordagem de summarização mostrando maior economia por requisição neste exemplo
