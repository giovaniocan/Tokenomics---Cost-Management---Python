# LLM Context Optimization

**English** · [Português](README.pt-BR.md)

> Practical comparison of token management strategies for LLM-based applications using Google Gemini and Python.

![LLM context optimization dashboard showing token savings across three strategies](docs/screenshots/dashboard.png)

## About

Managing the context window is critical for both cost efficiency and response quality in LLM-based applications. This project demonstrates and benchmarks three approaches to handling token constraints on a synthetic 50-message customer-support conversation, comparing offline token counting (tiktoken) against the actual count from the Google Gemini API.

## Features

- **Baseline comparison** — full conversation history submitted on every request
- **Context pruning** — drops oldest messages until fitting a token budget
- **Summarization buffer** — summarizes old messages via the API, keeps recent ones
- **Offline vs. online token counting** — compares tiktoken approximation against real API counts
- **Real API counts** — every strategy is measured with Gemini's `count_tokens` API, not estimated
- **Detailed metrics** — shows preserved message count, token savings, and cost breakdowns per strategy

## Sample output

The dashboard displays token counts for each strategy and shows savings when applied to the same conversation:

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

## Tech stack

- **Language:** Python 3.11+
- **LLM:** Google Gemini API (`gemini-2.5-flash-lite`)
- **Token counting:** tiktoken (OpenAI's tokenizer for offline reference)
- **Configuration:** python-dotenv

## Getting started

### Prerequisites

- Python 3.11 or higher
- A Google Gemini API key ([Google AI Studio](https://aistudio.google.com/apikey))

### Installation

```bash
git clone https://github.com/giovaniocan/Tokenomics---Cost-Management---Python.git
cd Tokenomics---Cost-Management---Python
pip install google-genai tiktoken python-dotenv
```

### Configuration

Create a `.env` file in the project root with your Gemini API key:

```bash
echo "GEMINI_API_KEY=your_key_here" > .env
```

### Run

```bash
python exercicio1.py
```

## Environment variables

| Variable | What it's for |
| --- | --- |
| `GEMINI_API_KEY` | Your Google Gemini API key |

## Key takeaways

- **Tiktoken ≠ Gemini tokenizer** — offline counting via tiktoken is an approximation; real API counts may differ
- **Pruning is simplest but lossy** — aggressive strategy removes messages to stay under budget; preserves only the most recent ones
- **Summarization retains more context** — combines a summary of old messages with recent ones, as shown in the dashboard
- **Measurable savings** — the dashboard demonstrates token reduction across strategies, with the summarization approach showing the largest per-request savings in this example
