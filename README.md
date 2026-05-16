# 🎬 Amnesia — Cinema

> Plataforma web de catálogo e avaliação de filmes, desenvolvida com FastAPI e MySQL.

---

## 📋 Sobre o Projeto

O **Amnesia** é uma aplicação web fullstack voltada para cinéfilos, onde usuários podem explorar um catálogo de filmes, avaliar títulos, gerenciar sua biblioteca pessoal e interagir com a comunidade através de comentários. Administradores têm acesso a um painel de controle com métricas e gerenciamento de conteúdo.

---

## ✨ Funcionalidades

- **Autenticação** — Cadastro e login com validação completa no front e back-end
- **Catálogo de Filmes** — Listagem com busca em tempo real, nota média e informações do diretor
- **Página de Detalhes** — Sinopse, elenco, gêneros e avaliações da comunidade
- **Avaliações** — Sistema de notas com comentário por usuário (upsert, uma avaliação por filme)
- **Minha Biblioteca** — Lista pessoal de filmes assistidos e filmes que deseja assistir
- **Editar Perfil** — Alteração de nome, senha e foto de avatar
- **Painel Admin** — Dashboard com métricas de usuários e filmes, gerenciamento de catálogo
- **Sessões JWT** — Tokens com renovação automática a cada requisição autenticada

---

## 🛠️ Stack

| Camada | Tecnologia |
|---|---|
| Back-end | Python 3.12+, FastAPI, Uvicorn |
| Banco de Dados | MySQL (via PyMySQL) |
| Templates | Jinja2 |
| Autenticação | JWT (PyJWT) + bcrypt |
| Sessões | Starlette SessionMiddleware (itsdangerous) |
| Front-end | HTML5, CSS3, JavaScript Vanilla |
| Ícones | Font Awesome 6 |

---

## 📁 Estrutura do Projeto

```
amnesia/
├── apps/
│   ├── auth/           # Login, cadastro e logout
│   ├── filmes/         # Listagem e detalhe de filmes
│   ├── avaliacoes/     # Submissão de notas e comentários
│   ├── meus_filmes/    # Biblioteca pessoal do usuário
│   ├── perfil/         # Edição de perfil e avatar
│   └── dashboard/      # Painel administrativo
├── core/
│   ├── security.py     # Hash de senha, JWT (criação/decodificação)
│   └── dependencies.py # Middleware de autenticação (get_current_user)
├── db/
│   ├── DB_Amnesia.sql  # Schema inicial
│   └── DB_Amnesia2.sql # Schema atualizado (tabela Usuario + Lista_Usuario)
├── static/
│   ├── css/            # Estilos por módulo
│   └── js/             # Scripts por módulo
├── templates/
│   ├── geral/menu.html # Header/nav reutilizável
│   └── *.html          # Templates por página
├── config.py           # Configuração do banco e JWT
├── main.py             # Entry point da aplicação
├── requirements.txt
└── .env.example
```

---

## ⚙️ Configuração

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/amnesia.git
cd amnesia
```

### 2. Instale dependências e configure os hooks

```bash
make setup
```

### 3. Configure as variáveis de ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```env
HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha
DATABASE=amnesia
SECRET_KEY=sua_chave_secreta_de_256_bits
```

> **Dica:** Para gerar uma `SECRET_KEY` segura, use `python -c "import secrets; print(secrets.token_hex(32))"`.

### 4. Crie o banco de dados

Execute o script mais recente no seu MySQL:

```bash
mysql -u root -p < db/DB_Amnesia2.sql
```

### 5. Inicie o servidor

```bash
make run
```

Acesse em: [http://localhost:8000](http://localhost:8000)

---

## 🗄️ Modelo de Dados (simplificado)

```
Usuario ─────┬──── Filme (AdicionadoPor_ID)
             ├──── Avaliacao (Usuario_ID + Filme_ID)
             └──── Lista_Usuario (Usuario_ID + Filme_ID)

Filme ────────┬──── Diretor (Diretor_ID)
              ├──── Filme_Ator ──── Ator_Atriz
              └──── Filme_Genero ── Genero
```

---

## 🔐 Rotas Principais

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Página de login/cadastro |
| `POST` | `/login` | Autenticar usuário |
| `POST` | `/cadastro` | Registrar novo usuário |
| `GET` | `/logout` | Encerrar sessão |
| `GET` | `/filmes` | Catálogo de filmes |
| `GET` | `/filmes/{id}` | Detalhes de um filme |
| `POST` | `/avaliar/{id}` | Submeter avaliação |
| `GET` | `/meus_filmes` | Biblioteca pessoal |
| `GET` | `/editar-perfil` | Formulário de perfil |
| `POST` | `/api/update-profile` | Atualizar nome de usuário |
| `POST` | `/api/change-password` | Alterar senha |
| `POST` | `/api/upload-avatar` | Enviar foto de perfil |
| `GET` | `/avatar/{user_id}` | Servir foto de perfil |
| `GET` | `/dashboard` | Painel admin (requer ADMIN) |

---

## 🧰 Comandos Disponíveis (Makefile)

```bash
make setup    # Instala dependências e configura hooks
make install  # Instala dependências
make run      # Inicia o servidor com hot-reload
make check    # Executa pre-commit em todos os arquivos
```

---

## 📝 Convenção de Commits

O projeto utiliza **Conventional Commits** via `pre-commit`. Exemplos de prefixos válidos:

```
feat: adiciona busca por gênero
fix: corrige erro no upload de avatar
refactor: separa lógica de autenticação
docs: atualiza README
```

---

## 👥 Tipos de Usuário

| Tipo | Permissões |
|---|---|
| `USER` | Explorar, avaliar, gerenciar biblioteca e perfil |
| `ADMIN` | Tudo acima + acesso ao painel admin e adição de filmes |