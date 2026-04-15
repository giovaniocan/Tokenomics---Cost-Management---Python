import os
from google import genai
from dotenv import load_dotenv
import tiktoken

load_dotenv()

client = genai.Client()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

# GERANDO AS 50 MENSAGENS (25 pares de pergunta/resposta)
conversation_history = []
for i in range(1, 26):
    conversation_history.append({"role": "user",      "content": f"Achei caro o serviço #{i}. Quero um reembolso."})
    conversation_history.append({"role": "assistant", "content": "Entendido. Vou verificar sua elegibilidade. Peço desculpas pelo atraso, vou escalar agora."})

texto_historico = "".join([f"{msg['role']}: {msg['content']}\n" for msg in conversation_history])

# Inicializar o contador de tokens offline
enc = tiktoken.get_encoding("cl100k_base")

# Função para contar tokens offline usando tiktoken
def count_tokens_offline(text):
    return len(enc.encode(text))

# Função para contar tokens online usando a API do Google Gemini
def count_tokens_online(messages):
    tokens = client.models.count_tokens(
        model="gemini-2.5-flash-lite",
        contents=messages
    )
    return tokens.total_tokens

# Função para contar tokens DEPOIS de ter feito a requisicao
def count_tokens_after_response(messages):
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=messages
    )
    return response.usage_metadata


# ==========================================
# SAÍDA FORMATADA NO CONSOLE
# ==========================================
print("\n" + "="*50)
print("📊 RELATÓRIO DE TOKENS (TESTE INICIAL)")
print("="*50)

print(f"🔹 Aproximado (Offline - Tiktoken): {count_tokens_offline(texto_historico)} tokens")
print(f"🔹 Exato (Online - API count_tokens): {count_tokens_online(texto_historico)} tokens")

# Pegando os metadados brutos
uso = count_tokens_after_response(texto_historico)

print("\n📉 Após a geração da resposta (API generate_content):")
print(f"   Input (Prompt Enviado):    {uso.prompt_token_count} tokens")
print(f"   Output (Resposta Gerada):  {uso.candidates_token_count} tokens")
print(f"   Total Gasto na Chamada:    {uso.total_token_count} tokens")
print("="*50 + "\n")


# ─────────────────────────────────────────────
# BLOCO 2 — CONTEXT PRUNING
# Mantém apenas as N últimas mensagens
# Estratégia mais simples e mais usada em prod
# ─────────────────────────────────────────────

MAX_HISTORY_TOKENS = 150

def prune_history(history: list, max_tokens: int) -> list:
    """
        Remove mensagens antigas até caber no budget.
        Sempre preserva as mensagens mais recentes ([-N:]).
    """
    pruned = history.copy()

    while True:
        text = "".join([m["content"] for m in pruned])
        current_tokens = count_tokens_online(text)

        if(current_tokens <= max_tokens):
            break
        
        if len(pruned) <= 2:
            break;
        pruned.pop(0)  # Remove a mensagem mais antiga (primeira da lista)

    removed = len(history) - len(pruned)
    return pruned


# Testando o pruning
pruned_history = prune_history(conversation_history, MAX_HISTORY_TOKENS)
tokens_pruned = count_tokens_online("".join([m["content"] for m in pruned_history]))


# ─────────────────────────────────────────────
# BLOCO 3 — SUMMARIZATION BUFFER COM GEMINI
# Quando pruning não basta: resume o histórico antigo
# com um modelo BARATO antes de mandar pro modelo principal
# ─────────────────────────────────────────────

def summatize_old_history(old_messages: list) -> str:
    """
        Recebe mensagens antigas e gera um resumo usando Gemini.
        O resumo é uma string que pode ser enviada como contexto para o modelo principal.
    """

    conversation_text  = "".join([f"{m['role']}: {m['content']}\n" for m in old_messages])

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=f"""
        Resume em 2-3 frases os pontos-chave desta conversa.
        Preserve: problemas mencionados, decisões tomadas, dados do cliente.
        Conversa:
        {conversation_text}"""
    )
    return response.text.strip()

def build_context_with_summary(history: list, keep_recent: int = 4) -> list:
    """
    Estratégia completa:
    1. Separa histórico em 'antigo' e 'recente'
    2. Resume o antigo (barato)
    3. Monta contexto final: [resumo] + [mensagens recentes]
    """

    if len(history) <= keep_recent:
        return history
    
    old_messages = history[:-keep_recent] # tudo exceto os últimos N
    recent_messages = history[-keep_recent:] # tudo exceto os últimos N

    summary = summatize_old_history(old_messages)

    context = [
        {
            "role": "user",
            "content": f"Resumo do histórico antigo:\n{summary}"
        }
    ] + recent_messages

    return context

# Testando a estratégia de summarization buffer
final_context = build_context_with_summary(conversation_history)
tokens_summary = count_tokens_online("".join([m["content"] for m in final_context]))


# ─────────────────────────────────────────────
# RELATÓRIO UNIFICADO PARA O LINKEDIN
# ─────────────────────────────────────────────

print("\n" + "═"*60)
print("🚀 LLM CONTEXT OPTIMIZATION DASHBOARD (50 MENSAGENS)")
print("═"*60)

print(f"\n1️⃣ BASELINE: ENVIO DO HISTÓRICO COMPLETO")
print(f"   ├─ Expectativa (Offline - Tiktoken): {count_tokens_offline(texto_historico)} tokens")
print(f"   └─ Custo Real (Online API):          {count_tokens_online(texto_historico)} tokens")

print("\n2️⃣ ESTRATÉGIA A: CONTEXT PRUNING")
print(f"   ├─ Mensagens preservadas: {len(pruned_history)} de {len(conversation_history)}")
print(f"   └─ Novo custo da chamada: {tokens_pruned} tokens")

print("\n3️⃣ ESTRATÉGIA B: SUMMARIZATION BUFFER (AGENTE RESUMIDOR)")
print(f"   ├─ Estrutura:             1 Resumo + {len(final_context)-1} Mensagens Recentes")
print(f"   ├─ Novo custo da chamada: {tokens_summary} tokens")
print(f"   └─ 💰 ECONOMIA TOTAL:     {count_tokens_online(texto_historico) - tokens_summary} tokens salvos por requisição!")
print("\n" + "═"*60 + "\n")