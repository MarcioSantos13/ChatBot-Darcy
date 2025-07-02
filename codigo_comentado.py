# ------------------------
# app.py — Chatbot Darcy
# ------------------------

from flask import Flask, render_template, request, jsonify  # Flask: framework web
from chatterbot import ChatBot                              # Módulo principal do ChatterBot
from chatterbot.trainers import ListTrainer                 # Treinador baseado em listas
import mysql.connector                                       # Biblioteca para conexão com MySQL
from fuzzywuzzy import fuzz                                 # Comparação de similaridade textual
import re                                                   # Expressões regulares

# 🔹 Inicializa a aplicação Flask
app = Flask(__name__)

# 🔹 Cria o chatbot "Darcy" usando o adaptador de armazenamento SQLite interno
chatbot = ChatBot(
    "Darcy",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    database_uri="sqlite:///database.sqlite3"
)

# 🔹 Cria o treinador para o fallback do ChatterBot
trainer = ListTrainer(chatbot)

# 🔧 Normaliza o texto recebido: minúsculas, sem pontuação
def normalizar_texto(texto):
    texto = texto.lower().strip()
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto

# 💾 Salva ou atualiza perguntas/respostas no banco MySQL
def salvar_interacao(pergunta, resposta):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chatbot_darcy",
            port=3306
        )
        cursor = conn.cursor()
        pergunta_normalizada = normalizar_texto(pergunta)

        # Verifica se já existe essa pergunta normalizada no banco
        cursor.execute(
            "SELECT resposta FROM chatbot_conversas WHERE pergunta_normalizada = %s",
            (pergunta_normalizada,)
        )
        resultado = cursor.fetchone()

        if resultado:
            # Atualiza pergunta e resposta
            cursor.execute(
                "UPDATE chatbot_conversas SET pergunta = %s, resposta = %s WHERE pergunta_normalizada = %s",
                (pergunta, resposta, pergunta_normalizada)
            )
        else:
            # Insere nova entrada
            cursor.execute(
                "INSERT INTO chatbot_conversas (pergunta, resposta, pergunta_normalizada) VALUES (%s, %s, %s)",
                (pergunta, resposta, pergunta_normalizada)
            )

        conn.commit()
        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        print(f"❌ Erro ao salvar no banco: {e}")

# 🌐 Página principal do chatbot
@app.route("/")
def home():
    return render_template("index.html")

# 🔁 Rota responsável por processar a pergunta do usuário e retornar resposta
@app.route("/get")
def get_response():
    user_message = request.args.get("msg", "")
    mensagem_limpa = normalizar_texto(user_message)

    try:
        # Conecta ao banco e recupera todas as perguntas cadastradas
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chatbot_darcy",
            port=3306
        )
        cursor = conn.cursor()
        cursor.execute("SELECT pergunta, resposta, pergunta_normalizada FROM chatbot_conversas")
        dados = cursor.fetchall()
        cursor.close()
        conn.close()

        melhor_resposta = None
        maior_score = 0

        # 🔎 Calcula a similaridade da entrada com perguntas do banco
        for pergunta_orig, resposta, pergunta_norm in dados:
            score_1 = fuzz.token_set_ratio(pergunta_norm, mensagem_limpa)
            score_2 = fuzz.partial_ratio(pergunta_norm, mensagem_limpa)
            score = (score_1 + score_2) / 2  # Combinação média de scores

            if score > maior_score and score >= 75:
                maior_score = score
                melhor_resposta = resposta

        # ✅ Retorna a melhor resposta baseada na similaridade
        if melhor_resposta:
            print(f"📌 [Fuzzy] Pergunta: \"{user_message}\" | Score: {maior_score:.1f}")
            return jsonify({"resposta": melhor_resposta})

        # 👋 Se a entrada for uma saudação isolada, responde com cumprimento
        elif mensagem_limpa.strip() in ["bom dia", "boa tarde", "boa noite", "oi", "olá", "ola"]:
            print(f"👋 [Saudação] Pergunta: \"{user_message}\"")
            return jsonify({"resposta": "Olá! Como posso te ajudar? 😊"})

        # 🤖 Se nada foi encontrado, usa o ChatterBot como fallback
        resposta_bot = chatbot.get_response(user_message)
        resposta_texto = str(resposta_bot) if resposta_bot else "Desculpe, não entendi sua pergunta."

        # Se a confiança do ChatterBot for baixa, dá uma resposta padrão
        if hasattr(resposta_bot, 'confidence') and resposta_bot.confidence < 0.5:
            resposta_texto = "Não tenho dados suficientes para responder, favor entrar em contato com o suporte pelo e-mail CEAD@UNB.BR"

        print(f"🧠 [Fallback] Pergunta: \"{user_message}\" | Resposta: \"{resposta_texto}\"")
        salvar_interacao(user_message, resposta_texto)
        return jsonify({"resposta": resposta_texto})

    except mysql.connector.Error as e:
        print(f"❌ [Erro MySQL] {e}")
        return jsonify({"resposta": f"Erro de banco de dados: {e}"})

    except Exception as e:
        print(f"❌ [Erro Geral] {e}")
        return jsonify({"resposta": f"Erro ao processar a resposta: {e}"})

# 🧠 Página de treinamento manual do chatbot
@app.route("/train_page")
def train_page():
    return render_template("train.html")

# 📝 Processa os dados de treinamento do formulário
@app.route("/train", methods=["POST"])
def train_chatbot():
    pergunta = request.form.get("pergunta")
    resposta = request.form.get("resposta")

    if pergunta and resposta:
        salvar_interacao(pergunta, resposta)
        return jsonify({"message": "✔ Treinamento realizado com sucesso!", "status": "success"})

    return jsonify({"message": "❌ Erro ao treinar chatbot.", "status": "error"})

# 📃 Lista todas as perguntas cadastradas no banco
@app.route("/list_questions")
def list_questions():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chatbot_darcy",
            port=3306
        )
        cursor = conn.cursor()
        cursor.execute("SELECT pergunta FROM chatbot_conversas")
        perguntas = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("list_questions.html", perguntas=perguntas)

    except mysql.connector.Error as e:
        return render_template("list_questions.html", perguntas=[], erro=f"Erro MySQL: {e}")
    except Exception as e:
        return render_template("list_questions.html", perguntas=[], erro=f"Erro inesperado: {e}")

# ▶️ Inicia o servidor Flask
if __name__ == "__main__":
    app.run(debug=True)
