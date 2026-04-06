import pymysql

# Configuração do banco de dados
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Henrique3103//",
    "database": "ClinicaSprint1"
}
# Função para obter conexão com MySQL
def get_db():
    return pymysql.connect(**DB_CONFIG)