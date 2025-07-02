from flask import Flask, render_template, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import mysql.connector
from fuzzywuzzy import fuzz
import re

app = Flask(__name__)

# Inicialização do ChatBot com adaptador de armazenamento
chatbot = ChatBot(
    "Darcy",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    database_uri="sqlite:///database.sqlite3"
)

trainer = ListTrainer(chatbot)

# 🔹 Normaliza o texto (lowercase e sem pontuação)
def normalizar_texto(texto):
    texto = texto.lower().strip()
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto

# 🔹 Salva ou atualiza uma pergunta no banco com a versão normalizada
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

        cursor.execute(
            "SELECT resposta FROM chatbot_conversas WHERE pergunta_normalizada = %s",
            (pergunta_normalizada,)
        )
        resultado = cursor.fetchone()

        if resultado:
            cursor.execute(
                "UPDATE chatbot_conversas SET pergunta = %s, resposta = %s WHERE pergunta_normalizada = %s",
                (pergunta, resposta, pergunta_normalizada)
            )
        else:
            cursor.execute(
                "INSERT INTO chatbot_conversas (pergunta, resposta, pergunta_normalizada) VALUES (%s, %s, %s)",
                (pergunta, resposta, pergunta_normalizada)
            )

        conn.commit()
        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        print(f"❌ Erro ao salvar no banco: {e}")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_response():
    user_message = request.args.get("msg", "")
    mensagem_limpa = normalizar_texto(user_message)

    try:
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

        for pergunta_orig, resposta, pergunta_norm in dados:
            score_1 = fuzz.token_set_ratio(pergunta_norm, mensagem_limpa)
            score_2 = fuzz.partial_ratio(pergunta_norm, mensagem_limpa)
            score = (score_1 + score_2) / 2

            if score > maior_score and score >= 75:
                maior_score = score
                melhor_resposta = resposta

        # 🎯 1. Tenta usar resposta por similaridade
        if melhor_resposta:
            return jsonify({"resposta": melhor_resposta})

        # 👋 2. Saudações simples — somente se a mensagem for exatamente isso
        elif mensagem_limpa.strip() in ["bom dia", "boa tarde", "boa noite", "oi", "olá", "ola"]:
            return jsonify({"resposta": "Olá! Como posso te ajudar? 😊"})

        # 🤖 3. Fallback: responder com ChatterBot ou mensagem padrão
        resposta_bot = chatbot.get_response(user_message)
        resposta_texto = str(resposta_bot) if resposta_bot else "Desculpe, não entendi sua pergunta."

        if hasattr(resposta_bot, 'confidence') and resposta_bot.confidence < 0.5:
            resposta_texto = "Não tenho dados suficientes para responder, favor entrar em contato com o suporte pelo e-mail CEAD@UNB.BR"

        salvar_interacao(user_message, resposta_texto)
        return jsonify({"resposta": resposta_texto})

    except mysql.connector.Error as e:
        return jsonify({"resposta": f"Erro de banco de dados: {e}"})
    except Exception as e:
        return jsonify({"resposta": f"Erro ao processar a resposta: {e}"})
@app.route("/train_page")
def train_page():
    return render_template("train.html")

@app.route("/train", methods=["POST"])
def train_chatbot():
    pergunta = request.form.get("pergunta")
    resposta = request.form.get("resposta")

    if pergunta and resposta:
        salvar_interacao(pergunta, resposta)
        return jsonify({"message": "✔ Treinamento realizado com sucesso!", "status": "success"})

    return jsonify({"message": "❌ Erro ao treinar chatbot.", "status": "error"})

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


if __name__ == "__main__":
    app.run(debug=True)
