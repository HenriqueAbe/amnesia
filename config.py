import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# Configuração do banco de dados
DB_CONFIG = {
    "host":     os.getenv("HOST","localhost"),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "Henrique3103//"),
    "database": os.getenv("DATABASE", "amnesia"),
}
# JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5

# Função para obter conexão com MySQL
def get_db():
    return pymysql.connect(**DB_CONFIG)