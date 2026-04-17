import pymysql

# Configuração do banco de dados
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Tper2012@1",
    "database": "amnesia"
}
# TODO: Alterar para .env
# JWT
SECRET_KEY = "4ab8e2f5d3d975bbdb8bd21c325438d10c2af6765b0f154b9122ad2551cece06"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

# Função para obter conexão com MySQL
def get_db():
    return pymysql.connect(**DB_CONFIG)