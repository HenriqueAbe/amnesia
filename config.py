import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# Configuração do banco de dados
DB_CONFIG = {
<<<<<<< Updated upstream
    "host": os.getenv("HOST"),
    "user": os.getenv("USER"),
    "password": os.getenv("PASSWORD"),
    "database": os.getenv("DATABASE")
=======
    "host":     os.getenv("HOST"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DATABASE"),
>>>>>>> Stashed changes
}
# TODO: Alterar para .env
# JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
<<<<<<< Updated upstream
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas
=======
ACCESS_TOKEN_EXPIRE_MINUTES = 500
>>>>>>> Stashed changes

# Função para obter conexão com MySQL
def get_db():
    return pymysql.connect(**DB_CONFIG)