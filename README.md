# 🎬 Movie Diary

Um app em Streamlit para buscar filmes no [TMDB](https://www.themoviedb.org/), dar nota
para os que você já assistiu e guardar tudo num banco SQLite local.

- **Buscar e avaliar** — procure pelo título, veja pôster, sinopse e gêneros, e dê uma
  nota de 0,5 a 10 com anotações e a data em que assistiu.
- **Minhas notas** — sua lista completa, com ordenação, edição e exclusão.

## Configuração

### 1. Pegue uma chave da API do TMDB (grátis)

1. Crie uma conta em [themoviedb.org](https://www.themoviedb.org/signup).
2. Vá em **Settings → API** e solicite uma chave (escolha *Developer*, uso pessoal).
3. Copie o valor da **API Key (v3 auth)**.

O formulário é aprovado na hora, sem análise manual. Para um projeto pessoal, pode
preencher assim: tipo de uso **Personal**, nome `Movie Diary`, URL
`http://localhost:8501` e um resumo de umas duas linhas explicando que é um app pessoal
para registrar suas notas.

### 2. Configure a chave

```powershell
Copy-Item .env.example .env
```

Abra o `.env` e troque `your_tmdb_api_key_here` pela sua chave. O `.env` está no
`.gitignore`, então a chave nunca vai parar num commit.

### 3. Ambiente virtual

A pasta `.venv/` já está criada e com tudo instalado. Se um dia precisar refazer:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Se o PowerShell bloquear o script de ativação, rode antes, no mesmo terminal:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

## Rodando

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

O app abre em http://localhost:8501. Sem ativar a venv, isso também funciona:

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

## Arquivos

| Arquivo | O que faz |
| --- | --- |
| `app.py` | Interface Streamlit — abas, resultados da busca, formulário de nota e listagem |
| `tmdb.py` | Cliente da API do TMDB (busca, detalhes, URLs dos pôsteres) |
| `database.py` | Schema e queries do SQLite (`movies.db`) |
| `.env` | Sua chave da API (fora do controle de versão) |
| `movies.db` | Suas notas — criado no primeiro uso, fora do controle de versão |

## Detalhes

- As respostas da API ficam em cache por uma hora, então repetir uma busca não gasta
  requisição à toa.
- É uma linha por filme: avaliar o mesmo filme de novo atualiza o registro existente.
- Para começar do zero, é só apagar o `movies.db`.
