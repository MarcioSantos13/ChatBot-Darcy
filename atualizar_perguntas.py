import mysql.connector
import re

def normalizar_texto(texto):
    texto = texto.lower().strip()
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="chatbot_darcy",
        port=3306
    )
    cursor = conn.cursor()

    cursor.execute("SELECT id, pergunta FROM chatbot_conversas WHERE pergunta_normalizada IS NULL OR pergunta_normalizada = ''")
    registros = cursor.fetchall()

    for id_pergunta, pergunta in registros:
        pergunta_limpa = normalizar_texto(pergunta)
        cursor.execute("UPDATE chatbot_conversas SET pergunta_normalizada = %s WHERE id = %s", (pergunta_limpa, id_pergunta))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Dados atualizados com sucesso!")

except mysql.connector.Error as e:
    print(f"❌ Erro ao conectar no banco: {e}")
