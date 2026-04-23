import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# Configuração do banco de dados
DB_CONFIG = {
    "host": os.getenv("HOST"),
    "user": os.getenv("USER"),
    "password": os.getenv("PASSWORD"),
    "database": os.getenv("DATABASE")
}
# TODO: Alterar para .env
# JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

# Função para obter conexão com MySQL
def get_db():
    return pymysql.connect(**DB_CONFIG)