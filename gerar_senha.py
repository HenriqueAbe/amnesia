# gerar_senha_admin.py
from core.security import hash_password

# A senha que você quer usar para o seu administrador
senha_admin = "administrador01@"

# Utiliza a própria função do seu sistema para gerar o hash
hash_gerado = hash_password(senha_admin)

print("=" * 60)
print(f"Senha original: {senha_admin}")
print("=" * 60)
print("Copie o HASH abaixo e cole no banco de dados (na coluna 'Senha'):\n")
print(hash_gerado)
print("\n" + "=" * 60)