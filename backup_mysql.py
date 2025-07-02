import os
import datetime
import subprocess

# 📁 Caminho onde o backup será salvo
PASTA_BACKUP = "backups"
NOME_BANCO = "chatbot_darcy"
USUARIO = "root"
SENHA = ""
HOST = "localhost"
PORTA = "3306"

# 🕒 Gera nome do arquivo com data e hora
agora = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
nome_arquivo = f"{NOME_BANCO}_backup_{agora}.sql"

# Cria pasta de backup se não existir
if not os.path.exists(PASTA_BACKUP):
    os.makedirs(PASTA_BACKUP)

# 📦 Caminho completo do backup
caminho_arquivo = os.path.join(PASTA_BACKUP, nome_arquivo)

# 🧠 Comando do mysqldump
comando = [
    "mysqldump",
    f"-h{HOST}",
    f"-P{PORTA}",
    f"-u{USUARIO}",
    f"-p{SENHA}",
    NOME_BANCO
]

# Abre o arquivo para escrita do backup
with open(caminho_arquivo, "w", encoding="utf-8") as arquivo_saida:
    processo = subprocess.Popen(comando, stdout=arquivo_saida, stderr=subprocess.PIPE, shell=False)
    _, erro = processo.communicate()

if processo.returncode == 0:
    print(f"✅ Backup criado com sucesso em: {caminho_arquivo}")
else:
    print(f"❌ Erro ao criar o backup: {erro.decode()}")
