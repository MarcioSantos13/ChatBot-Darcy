import mysql.connector

def conectar():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chatbot_darcy",
            port=3306
        )
        print("Conexão bem-sucedida!")
        return conn
    except mysql.connector.Error as erro:
        print(f"Erro ao conectar ao MySQL: {erro}")
        return None

