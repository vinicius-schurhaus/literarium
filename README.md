# Literarium

Sistema web de **gerenciamento de biblioteca escolar**. Permite que alunos pesquisem o
acervo, peçam empréstimos, façam reservas e escrevam resenhas, enquanto a equipe da
biblioteca cadastra livros, controla empréstimos/devoluções e gera relatórios.

O projeto é dividido em duas partes que rodam separadas:

- **Backend** — uma API em **Django + Django REST Framework** que guarda os dados
  (livros, alunos, empréstimos…) num banco **SQLite** e expõe tudo em `/api/`.
- **Frontend** — uma aplicação **React (Vite)** que roda no navegador e consome essa API.

> Se você nunca mexeu no projeto, siga a seção [**Rodando localmente**](#rodando-localmente)
> do começo ao fim — ela assume que você está partindo do zero.

---

## Índice

- [O que o sistema faz](#o-que-o-sistema-faz)
- [Como funciona (arquitetura)](#como-funciona-arquitetura)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Pré-requisitos](#pré-requisitos)
- [Rodando localmente](#rodando-localmente)
- [Perfis de usuário](#perfis-de-usuário)
- [Rodando com Docker (alternativa)](#rodando-com-docker-alternativa)
- [Testes](#testes)
- [Deploy em produção](#deploy-em-produção-render-custo-zero)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Segurança](#segurança)

---

## O que o sistema faz

- **Catálogo** de livros com busca, filtro por gênero e paginação.
- **Empréstimos** com controle de estoque seguro (sem condição de corrida).
- **Reservas** de livros esgotados, com cálculo automático da próxima data disponível.
- **Renovação** de empréstimos (+7 dias, respeitando reservas ativas).
- **Resenhas e notas** dos alunos sobre os livros.
- **Filtro de conteúdo explícito** por turma (controle de classificação indicativa).
- **Troca de senha** pelo próprio usuário.
- **Relatórios** de empréstimos e devoluções por período, com exportação em CSV.
- **Painel administrativo** do Django (`/admin`) para cadastros e gestão avançada.

## Como funciona (arquitetura)

| Camada | Tecnologia |
|---|---|
| Backend | Django 5 + Django REST Framework + SimpleJWT |
| Banco de dados | SQLite (arquivo `db.sqlite3`, criado automaticamente) |
| Frontend | React 19 + Vite + Tailwind CSS + shadcn/ui |
| Comunicação | HTTP/JSON; autenticação via **JWT** no header `Authorization: Bearer <token>` |

Em **desenvolvimento** você roda **dois processos ao mesmo tempo**: o backend Django na
porta `8000` e o frontend Vite na porta `5173`. O Vite encaminha automaticamente as
chamadas `/api` e `/media` para o backend, então você não precisa configurar URLs.

Em **produção** (Render) tudo roda em **um único serviço**: o Django serve a API e o build
do React na mesma origem, então não há configuração de URLs nem CORS.

## Estrutura de pastas

```
literarium/
├── core/              # App Django principal: modelos, API, regras de negócio, testes
│   ├── models.py        # Livro, Aluno, Emprestimo, Reserva, Resenha, Genero, Autor, Turma
│   ├── services.py      # Regras de negócio (emprestar, devolver, reservar, renovar)
│   ├── serializers.py   # Conversão modelo <-> JSON da API
│   ├── api_views.py     # Endpoints da API REST
│   ├── api_urls.py      # Rotas da API (/api/...)
│   ├── admin.py         # Painel /admin do Django
│   └── tests/           # Testes automatizados do backend
├── literarium/        # Configuração do projeto Django (settings, urls, wsgi)
├── frontend/          # Aplicação React (Vite)
│   └── src/             # Páginas, componentes, chamadas de API, autenticação
├── manage.py          # CLI do Django (migrate, runserver, test...)
├── requirements.txt   # Dependências do backend (Python)
├── Dockerfile         # Imagem do backend
└── docker-compose.yml # Sobe o backend em container (alternativa ao venv)
```

## Pré-requisitos

Instale antes de começar:

- **Python 3.10 ou superior** — <https://www.python.org/downloads/>
- **Node.js 20 ou superior** (vem com o `npm`) — <https://nodejs.org/>
- **Git** — <https://git-scm.com/>

Confira as versões instaladas:

```bash
python --version
node --version
```

---

## Rodando localmente

Você vai precisar de **dois terminais abertos**: um para o backend, outro para o frontend.

### Passo 1 — Clonar o projeto

```bash
git clone <url-do-repositorio> literarium
cd literarium
```

### Passo 2 — Backend (terminal 1)

**2.1. Crie e ative um ambiente virtual** (isola as dependências Python do projeto):

```bash
python -m venv .venv

# Ative-o:
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate
```

Quando ativo, o prompt do terminal mostra `(.venv)` no início.

**2.2. Instale as dependências do backend:**

```bash
pip install -r requirements.txt
```

**2.3. Crie o arquivo `.env`** na raiz do projeto. Copie o modelo e edite:

```bash
# Windows: copy .env.example .env
# Linux/macOS:
cp .env.example .env
```

Para desenvolvimento, o conteúdo mínimo é:

```env
SECRET_KEY=qualquer-chave-para-desenvolvimento
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Gere uma `SECRET_KEY` de verdade com:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**2.4. Crie o banco de dados** (o SQLite é criado automaticamente):

```bash
python manage.py migrate
```

**2.5. Crie um usuário administrador** (você vai usá-lo para entrar no sistema):

```bash
python manage.py createsuperuser
```

Informe um nome de usuário e senha — guarde-os.

**2.6. Suba o servidor do backend:**

```bash
python manage.py runserver
```

Deixe esse terminal rodando. A API fica em <http://localhost:8000/api/> e o painel
administrativo em <http://localhost:8000/admin/>.

### Passo 3 — Frontend (terminal 2)

Em **outro terminal**, na raiz do projeto:

```bash
cd frontend
npm install        # instala as dependências (só na primeira vez)
npm run dev        # sobe o frontend
```

Abra <http://localhost:5173> no navegador.

### Passo 4 — Entrar no sistema

Na tela de login, use o **usuário administrador** criado no passo 2.5. Como ele é da
equipe (`is_staff`), você verá o **painel de gestão** (cadastro de livros, alunos,
empréstimos, relatórios etc.).

Para testar o **portal do aluno**, crie um aluno conforme a próxima seção.

---

## Perfis de usuário

O sistema tem dois tipos de usuário, e a interface se adapta a cada um:

| Perfil | Como identificar | O que vê |
|---|---|---|
| **Equipe / Gestão** | usuário com `is_staff` (ex.: o superusuário) | Painel de gestão (`/staff/...`): livros, alunos, empréstimos, reservas, resenhas, relatórios |
| **Aluno** | usuário com perfil de aluno vinculado | Portal do aluno: catálogo, pesquisa, livros populares, "Meus empréstimos" |

**Como criar um aluno:**

1. Acesse <http://localhost:8000/admin/> e entre com o superusuário.
2. Vá em **Alunos → Adicionar**.
3. Preencha nome de usuário, nome, matrícula, turma e uma senha.
4. Salve. Esse aluno agora consegue entrar em <http://localhost:5173> com o usuário e a
   senha definidos.

> Turmas e gêneros também são cadastrados pelo `/admin`. A turma define se o aluno pode
> ver livros marcados como conteúdo explícito.

---

## Rodando com Docker (alternativa)

Se preferir não instalar Python localmente, suba **apenas o backend** em container
(o frontend continua sendo rodado com `npm run dev`):

```bash
# precisa de um .env na raiz (mesmo do passo 2.3)
docker compose up --build
```

O backend sobe com **gunicorn** na porta `8000`, já rodando `migrate` e `collectstatic`
automaticamente (ver `entrypoint.sh`). Os uploads de mídia ficam na pasta local `media/`.

---

## Testes

```bash
# Backend (na raiz, com o venv ativo)
python manage.py test core

# Com cobertura
coverage run manage.py test core && coverage report -m

# Frontend
cd frontend
npm test
```

---

## Deploy em produção (Render, custo zero)

No Render o deploy é **combinado em um único serviço**: o Django serve a API **e** o build
do React (via WhiteNoise) na mesma URL. Isso elimina CORS e dispensa um segundo serviço.
O banco é um **PostgreSQL gerenciado** do próprio Render. Tudo no plano **Free**.

Arquivos que sustentam esse deploy (já no repositório):
- `Dockerfile` — build multi-stage: estágio Node compila o React, estágio Python roda o Django.
- `render.yaml` — Blueprint que cria o Postgres e o Web Service e liga as variáveis.
- `entrypoint.sh` — roda `migrate`, `collectstatic` e `seed_demo` e sobe o Gunicorn em `$PORT`.
- `core/management/commands/seed_demo.py` + `seed/initial_data.json` + `seed_media/` — semeiam o
  catálogo inicial, as capas e o superusuário (idempotente, roda a cada boot).

### Passo a passo (Blueprint — recomendado)

1. Faça `git push` com tudo commitado.
2. No [dashboard do Render](https://dashboard.render.com): **New +** → **Blueprint**.
3. Conecte o GitHub e selecione este repositório. O Render lê o `render.yaml` e propõe
   **literarium-db** (Postgres free) + **literarium** (Web Service Docker free).
4. Preencha os 3 segredos pedidos: `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD`,
   `DJANGO_SUPERUSER_EMAIL`. (`SECRET_KEY` e `DATABASE_URL` são preenchidos automaticamente.)
5. **Apply**. O Render builda a imagem e roda o `entrypoint.sh`. Ao terminar, abra a URL
   pública (ex.: `https://literarium.onrender.com`) — SPA, `/api/` e `/admin/` na mesma origem.

> `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` são resolvidos sozinhos a partir de
> `RENDER_EXTERNAL_HOSTNAME` (ver `literarium/settings.py`) — não precisa configurar domínio.

### Alternativa manual (sem Blueprint)

1. **New + → PostgreSQL** (plano **Free**). Copie a **Internal Database URL**.
2. **New + → Web Service** → conecte o repo → **Runtime: Docker** → plano **Free**.
3. Em **Environment**, adicione: `DATABASE_URL` (a do passo 1), `SECRET_KEY`, `DEBUG=False`,
   `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD`, `DJANGO_SUPERUSER_EMAIL`.
4. **Create Web Service** e acompanhe os logs.

Pós-deploy: a aba **Shell** do serviço permite rodar comandos (`python manage.py createsuperuser` etc.).

### Limitações do plano Free do Render

- **Postgres free expira ~30 dias** após criado (depois é suspenso/excluído). Recrie o banco
  (o `seed_demo` repovoa o catálogo) ou faça upgrade quando quiser persistência longa.
- O Web Service **hiberna após ~15 min** de inatividade — o 1º acesso depois disso leva ~30–60s.
- **Uploads novos de capa** (pelo admin) somem no próximo redeploy, pois o disco é efêmero.
  Persistem apenas as capas versionadas em `seed_media/`. Para uploads persistentes seria preciso
  um disco pago do Render ou um storage externo (ex.: Cloudinary).

> Com `DEBUG=False`, o Django ativa o reforço de segurança HTTPS (HSTS, redirect, cookies
> seguros). Valide com `python manage.py check --deploy`.

---

## Variáveis de ambiente

**Backend** (arquivo `.env` na raiz — veja `.env.example`):

| Variável | Obrigatória | Descrição |
|---|---|---|
| `SECRET_KEY` | Sim (fora de testes) | Chave secreta do Django. Gere uma única por ambiente. |
| `DEBUG` | Não (padrão `False`) | `True` em dev; `False` em produção (ativa o hardening HTTPS). |
| `ALLOWED_HOSTS` | Não | Domínios do backend, separados por vírgula. |
| `CORS_ALLOWED_ORIGINS` | Não | URL(s) do frontend autorizadas a chamar a API. |
| `CSRF_TRUSTED_ORIGINS` | Não | URL do backend, para o `/admin` sob HTTPS. |
| `DATABASE_URL` | Não | Se ausente, usa SQLite. Para outro banco, instale o driver correspondente. |

**Frontend** (arquivo `frontend/.env` — veja `frontend/.env.example`):

| Variável | Descrição |
|---|---|
| `VITE_API_URL` | URL da API em produção (ex.: `https://.../api`). Em dev pode ficar em branco — o proxy do Vite cuida disso. |

---

## Segurança

- A `SECRET_KEY` é lida do ambiente; o servidor recusa subir sem ela (exceto em testes).
- Com `DEBUG=False`, ativam-se HSTS, redirect HTTPS, cookies seguros e `nosniff`.
- Autenticação por token Bearer (a API não usa cookies de sessão → sem CSRF na API).
- Throttling de requisições (anônimas e autenticadas) configurado no DRF.
- `ALLOWED_HOSTS` e `CORS_ALLOWED_ORIGINS` restritos por ambiente.
- O arquivo `.env` está no `.gitignore` — **nunca** o adicione ao versionamento e use uma
  `SECRET_KEY` diferente em produção.
