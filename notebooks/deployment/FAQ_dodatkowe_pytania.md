# FAQ - Dodatkowe pytania o deployment

## 1. Django vs Flask - Development Server

**Pytanie:** A Django nie ma tego samego co Flask - werkzeug? Jeżeli nie, to co ma?

**Odpowiedź:**

**NIE**, Django **nie używa** Werkzeug.

### Flask:
- Development server: **Werkzeug** (biblioteka WSGI utilities)
- Werkzeug to część ekosystemu Flask (ten sam autor - Armin Ronacher)
- `flask run` → uruchamia Werkzeug development server

### Django:
- Development server: **własny wbudowany server** (w module `django.core.servers.basehttp`)
- Bazuje na **`wsgiref`** z Python standard library
- `python manage.py runserver` → uruchamia Django's development server

### Szczegóły:

```python
# Flask (używa Werkzeug)
from flask import Flask
app = Flask(__name__)

# Kiedy robisz: flask run
# Uruchamia: werkzeug.serving.run_simple()

# Django (własny server)
# Kiedy robisz: python manage.py runserver
# Uruchamia: django.core.servers.basehttp.ServerHandler
# Który bazuje na: wsgiref.simple_server z Python stdlib

# FastAPI (używa Uvicorn)
from fastapi import FastAPI
app = FastAPI()

# Kiedy robisz: uvicorn main:app --reload
# Uruchamia: Uvicorn (ASGI server)
# Który bazuje na: uvloop/httptools (async I/O)
```

### Kluczowa różnica:

| Framework | Development Server | Bazuje na |
|-----------|-------------------|-----------|
| **Flask** | Werkzeug | Własna implementacja WSGI |
| **Django** | django.core.servers | wsgiref (Python stdlib) |
| **FastAPI** | Uvicorn | ASGI (async) |

**Obie są tylko do development!** W produkcji używasz Gunicorn/uWSGI/Uvicorn.

---

## 2. Pure-Python WSGI Servers

**Pytanie:** Jeżeli Waitress to pure-python WSGI server, to co Gunicorn, mod_wsgi, uWSGI nie są pure-python? Myślałem że WSGI to ściśle pythonowa technologia (stworzona na i dla Pythona).

**Odpowiedź:**

Świetne pytanie! **WSGI jest pythonową technologią**, ale **implementacje** mogą mieć komponenty w C dla performance.

### Wyjaśnienie:

**WSGI (standard)** = 100% pythonowa koncepcja (PEP 3333)

**Implementacje WSGI servers:**

| Server | Pure-Python? | Szczegóły |
|--------|--------------|-----------|
| **Waitress** | ✅ TAK | 100% Python - wszystko w Pythonie |
| **Gunicorn** | ✅ TAK | 100% Python (choć używa C extensions dla performance w niektórych miejscach, ale są opcjonalne) |
| **uWSGI** | ❌ NIE | Napisany w C, Python to tylko interfejs |
| **mod_wsgi** | ❌ NIE | Apache module w C |

### Dlaczego "pure-Python" ma znaczenie?

```
Pure-Python (Waitress, Gunicorn):
✅ Łatwa instalacja (pip install waitress)
✅ Działa wszędzie gdzie jest Python
✅ Nie wymaga kompilatora C
✅ Łatwy debugging (cały kod w Pythonie)
❌ Może być wolniejszy

Non-pure-Python (uWSGI):
✅ Szybszy (C optimizations)
✅ Więcej features (process management w C)
❌ Trudniejsza instalacja (wymaga gcc/kompilator)
❌ Trudniejszy debugging
❌ Zależności systemowe
```

### Przykład:

```bash
# Waitress - pure Python
pip install waitress  # Zawsze działa, nie wymaga kompilatora

# uWSGI - wymaga C compiler
pip install uwsgi  # Może się nie udać jeśli brak gcc!
# Error: unable to execute 'gcc': No such file or directory
```

### Podsumowanie:

- **WSGI** = pythonowa technologia (standard)
- **Pure-Python WSGI server** = implementacja w 100% w Pythonie (bez C extensions)
- **Non-pure-Python** = używa C dla performance, ale nadal implementuje pythonowy standard WSGI

**Waitress** jest marketowany jako "pure-Python" bo:
1. Nie wymaga kompilatora C
2. Łatwy deployment (szczególnie na Windows)
3. Mniej zależności systemowych

---

## 3. (brak pytania)

---

## 4. HTTP Server - Statyczny vs Dynamiczny

**Pytanie:** Pierwszy rozdział zatytułowałeś "HTTP Server - tradycyjny (statyczny)", tzn. co, może być serwer HTTP dynamiczny? Jeżeli tak, to jaki to będzie i czym się różni od takiego serwera HTTP statycznego z WSGI mode?

**Odpowiedź:**

Świetne pytanie! Tytuł rzeczywiście może mylić. Wyjaśniam:

### Terminologia (moje nazewnictwo):

- **"Tradycyjny/statyczny HTTP server"** = serwuje **pliki z dysku** (nginx, Apache w podstawowym trybie)
- **"HTTP server z WSGI mode"** = HTTP server + moduł WSGI (Apache + mod_wsgi)

### Ale właściwie:

**Nie ma czegoś takiego jak "dynamiczny HTTP server"** - to nieprecyzyjne określenie.

Lepsze rozróżnienie:

### 1. HTTP Server bez WSGI/ASGI:
```
nginx (basic config)
├─ /index.html → czyta z dysku
├─ /style.css → czyta z dysku
└─ /image.png → czyta z dysku

Tylko static files!
```

### 2. HTTP Server + WSGI Module (Apache + mod_wsgi):
```
Apache + mod_wsgi
├─ /static/style.css → czyta z dysku (static)
└─ /api/users → wywołuje Python funkcję przez WSGI (dynamic)

Serwuje static files + uruchamia Python!
```

### 3. HTTP Server jako Reverse Proxy (nginx + Gunicorn):
```
nginx (reverse proxy)
├─ /static/ → czyta z dysku (nginx serwuje)
└─ /api/ → forward → Gunicorn (WSGI server) → Python app

nginx nie uruchamia Pythona - przekazuje request dalej!
```

### Różnica kluczowa:

| Setup | Czym jest HTTP Server | Kto uruchamia Python |
|-------|----------------------|---------------------|
| **Apache + mod_wsgi** | HTTP Server + WSGI server w jednym | Apache (przez mod_wsgi) |
| **nginx + Gunicorn** | HTTP Server (reverse proxy) | Gunicorn (oddzielny proces) |

### Co jest lepsze?

**Apache + mod_wsgi:**
```
✅ Wszystko w jednym procesie
❌ Tightly coupled (restart Apache = restart app)
❌ Trudniejszy deployment
```

**nginx + Gunicorn (oddzielnie):**
```
✅ Separacja concerns (nginx = proxy, Gunicorn = app)
✅ Łatwy deployment (restart app bez restartu nginx)
✅ Lepsze resource management
⭐ RECOMMENDED dla nowoczesnych aplikacji
```

### Podsumowanie:

Nie używaj terminów "statyczny/dynamiczny HTTP server".

**Lepiej:**
- **HTTP Server** (nginx, Apache) - serwuje pliki z dysku
- **HTTP Server + WSGI module** (Apache + mod_wsgi) - serwuje pliki + uruchamia Python
- **HTTP Server + Reverse Proxy** (nginx + Gunicorn) - przekazuje requesty do WSGI servera

**Nowoczesny standard:** nginx (reverse proxy) + Gunicorn/Uvicorn (WSGI/ASGI server)

---

## 5. HTTP Server + WSGI Server - Jak to działa?

**Pytanie:** To rozumiem, że żeby aplikacja działała to musi być postawiony serwer HTTP i uruchomiony serwer WSGI, tak? I to zawsze działa w ten sposób? Jeżeli tak, to jak uruchamiam Django, to domyślnie jaki serwer HTTP się uruchamia i jaki serwer WSGI?

**Odpowiedź:**

### Kluczowa odpowiedź:

**NIE zawsze są oddzielne!** W development często są **w jednym procesie**.

### Opcje architektur:

#### 1. Development (Django/Flask):
```
python manage.py runserver

Uruchamia SIĘ:
┌─────────────────────────────┐
│  Django development server  │
│  ┌────────────┬───────────┐ │
│  │ HTTP Server│WSGI Server│ │  ← W JEDNYM procesie!
│  │ (wsgiref)  │ (wsgiref) │ │
│  └────────────┴───────────┘ │
└─────────────────────────────┘
```

**Jeden proces = HTTP Server + WSGI Server razem!**

#### 2. Production Option A (Apache + mod_wsgi):
```
Apache + mod_wsgi

┌──────────────────────────┐
│       Apache             │
│  ┌──────────┬─────────┐  │
│  │HTTP Server│mod_wsgi│  │  ← W JEDNYM procesie!
│  │          │(WSGI)   │  │
│  └──────────┴─────────┘  │
└──────────────────────────┘
```

**Jeden proces = HTTP Server + WSGI Server razem!**

#### 3. Production Option B (nginx + Gunicorn) - RECOMMENDED:
```
nginx + Gunicorn

┌──────────────┐         ┌────────────────┐
│    nginx     │  HTTP   │   Gunicorn     │
│ (HTTP Server)│ ──────> │ (WSGI Server)  │  ← DWA oddzielne procesy!
│ port 80/443  │         │ port 8000      │
└──────────────┘         └────────────────┘
```

**Dwa procesy:**
1. nginx (HTTP Server + Reverse Proxy)
2. Gunicorn (WSGI Server + Python app)

### Django `runserver` - szczegóły:

```bash
python manage.py runserver
# Starting development server at http://127.0.0.1:8000/
```

**Co się uruchamia:**

| Komponent | Implementacja | Plik |
|-----------|---------------|------|
| **HTTP Server** | wsgiref.simple_server (Python stdlib) | django/core/servers/basehttp.py |
| **WSGI Server** | wsgiref.simple_server (Python stdlib) | django/core/servers/basehttp.py |

**Oba w jednym procesie!**

Kod (uproszczony):
```python
# django/core/servers/basehttp.py
from wsgiref import simple_server

class WSGIServer(simple_server.WSGIServer):
    """Django's development server (HTTP + WSGI)"""
    pass

# Jeden proces obsługuje:
# 1. HTTP (przyjmowanie requestów)
# 2. WSGI (wywołanie Python funkcji)
```

### FastAPI development:

```bash
uvicorn main:app --reload
```

**Co się uruchamia:**

| Komponent | Implementacja |
|-----------|---------------|
| **HTTP Server** | Uvicorn (httptools/uvloop) |
| **ASGI Server** | Uvicorn |

**Oba w jednym procesie!** (Uvicorn = HTTP + ASGI razem)

### Podsumowanie:

| Setup | Ile procesów | Komponenty |
|-------|-------------|------------|
| **Django runserver** | 1 | HTTP Server + WSGI Server (wsgiref) |
| **Flask run** | 1 | HTTP Server + WSGI Server (Werkzeug) |
| **Uvicorn** | 1 | HTTP Server + ASGI Server |
| **Apache + mod_wsgi** | 1 | HTTP Server + WSGI Server (mod_wsgi) |
| **nginx + Gunicorn** | 2 | nginx (HTTP) + Gunicorn (WSGI) ⭐ RECOMMENDED |

### Czy zawsze musi być HTTP Server + WSGI Server?

**TAK**, ale mogą być:
- **W jednym procesie** (development, Apache + mod_wsgi)
- **W oddzielnych procesach** (nginx + Gunicorn) ← lepsze dla produkcji

### Django runserver - dokładnie:

```bash
python manage.py runserver

Uruchamia:
1. wsgiref.simple_server (HTTP + WSGI w jednym)
2. Na porcie 8000
3. TYLKO DLA DEVELOPMENT (single-threaded, brak security, wolny)
```

W produkcji:
```bash
# Oddzielnie nginx + Gunicorn
nginx  # port 80 (HTTP Server + Reverse Proxy)
gunicorn myproject.wsgi:application  # port 8000 (WSGI Server)
```

---

## 6. async def w WSGI vs def w ASGI

**Pytanie:** W WSGI vs ASGI - co jeżeli w WSGI zrobię widok `async def ...`, albo w ASGI widok `def ...`, czymś się to od siebie będzie różniło w praktyce?

**Odpowiedź:**

BARDZO dobre pytanie! To pokazuje różnicę między **framework capability** a **server capability**.

### Scenariusz 1: `async def` widok w WSGI server

```python
# FastAPI (ASGI app) z async endpoint
# ALE uruchomione na WSGI server (Gunicorn bez Uvicorn workers)
from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/api/data")
async def get_data():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.example.com')
    return {'data': response.json()}

# ❌ Uruchomione na CZYSTYM Gunicorn (WSGI) - NIE ZADZIAŁA!
# gunicorn main:app --workers 4
# Error: FastAPI wymaga ASGI server!

# Przykład z Django (który może działać na WSGI):
# from django.http import JsonResponse
# async def my_view(request):
#     async with httpx.AsyncClient() as client:
#         response = await client.get('https://api.example.com')
#     return JsonResponse({'data': response.json()})
#
# gunicorn myproject.wsgi:application --workers 4
```

**Co się stanie:**

**FastAPI:**
❌ **NIE ZADZIAŁA** - FastAPI to ASGI framework, Gunicorn (czysty) to WSGI server
- Musisz użyć: `gunicorn main:app --worker-class uvicorn.workers.UvicornWorker`

**Django (dla porównania):**
✅ **Zadziała** (Django 3.0+ wspiera async views)
⚠️ **ALE** - worker jest **zablokowany** podczas całego requesta!

**Dlaczego Django na WSGI blokuje?**

```
WSGI server (Gunicorn)
  ↓
Dostaje request
  ↓
Wywołuje Django (synchronicznie)
  ↓
Django widzi: async def my_view
  ↓
Django robi: asyncio.run(my_view(request))  ← Blokuje cały worker!
  ↓
Async widok się wykonuje wewnętrznie async, ALE worker jest zablokowany
```

**Efekt - co ZYSKUJESZ:**
✅ **Concurrent I/O w obrębie JEDNEGO requesta** - jeśli w widoku robisz wiele operacji I/O (np. 3 API calls), mogą wykonać się równolegle
```python
# To BĘDZIE szybsze nawet na WSGI!
results = await asyncio.gather(
    client.get('api1'),  # 1s
    client.get('api2'),  # 1s
    client.get('api3'),  # 1s
)
# Zajmie ~1s (nie 3s!) ✅ KORZYŚĆ!
```

**Efekt - co TRACISZ:**
❌ **Concurrent REQUESTS handling** - worker jest zablokowany podczas całego requesta
- Podczas `await` worker NIE MOŻE obsłużyć innych requestów
- Inne requesty muszą czekać na wolny worker
- **To jest główna stracona korzyść!**

**Podsumowanie:**
- ✅ Jeden request może być szybszy (concurrent I/O wewnętrznie)
- ❌ Worker nie może obsługiwać innych requestów podczas await (blokuje throughput)
- **FastAPI w ogóle nie zadziała** na czystym WSGI serverze

### Scenariusz 2: `def` (sync) widok w ASGI server

```python
# FastAPI (ASGI) z sync view
from fastapi import FastAPI
import time

app = FastAPI()

@app.get("/slow")
def slow_endpoint():
    time.sleep(5)  # Synchroniczne blokowanie
    return {"status": "done"}

# Uruchomione na Uvicorn (ASGI)
# uvicorn main:app --workers 4
```

**Co się stanie:**

✅ **Zadziała**
❌ **ALE** - sync widok będzie **blokował cały worker**!

**Dlaczego?**

```
ASGI server (Uvicorn)
  ↓
Dostaje request
  ↓
Wywołuje FastAPI (asynchronicznie)
  ↓
FastAPI widzi: def slow_endpoint (sync)
  ↓
FastAPI robi: await run_in_threadpool(slow_endpoint)  ← uruchamia w thread pool
  ↓
ALE time.sleep(5) blokuje thread na 5 sekund
```

**Efekt:**
- Sync widok działa
- ALE używa thread pool (overhead)
- **Mniej efektywne** niż gdyby było async

### Praktyczne różnice:

#### Test 1: async view w WSGI (Django + Gunicorn)

```python
# views.py
import httpx
import asyncio

async def api_call(request):
    async with httpx.AsyncClient() as client:
        await client.get('https://api.example.com')  # 1 sekunda
    return JsonResponse({})

# Gunicorn (WSGI) z 1 workerem
# Request 1 przychodzi -> blokuje worker na 1 sek
# Request 2 przychodzi -> CZEKA aż Request 1 się skończy
# Throughput: 1 request/sekundę
```

#### Test 2: async view w ASGI (FastAPI + Uvicorn)

```python
# main.py
import httpx

@app.get("/api")
async def api_call():
    async with httpx.AsyncClient() as client:
        await client.get('https://api.example.com')  # 1 sekunda
    return {}

# Uvicorn (ASGI) z 1 workerem
# Request 1 przychodzi -> await (nie blokuje)
# Request 2 przychodzi -> await (nie blokuje)
# Request 3 przychodzi -> await (nie blokuje)
# Throughput: setki requestów/sekundę (concurrent I/O!)
```

#### Test 3: sync view w ASGI (FastAPI + Uvicorn)

```python
import time

@app.get("/sync")
def sync_endpoint():
    time.sleep(1)  # Blokujące!
    return {}

# Uvicorn (ASGI) z 1 workerem
# Request 1 -> uruchamia w thread pool -> blokuje thread
# Request 2 -> uruchamia w innym thread -> blokuje inny thread
# Thread pool ma limit (domyślnie 40 threads)
# Throughput: ~40 requestów/sekundę (limit thread pool)
```

### Podsumowanie tabela:

| Framework | Server | Widok | Czy działa? | Efektywność |
|-----------|--------|-------|-------------|-------------|
| Django | Gunicorn (WSGI) | `async def` | ✅ TAK | ❌ Blokuje worker |
| Django | Uvicorn (ASGI) | `async def` | ✅ TAK | ✅ Async I/O! |
| Django | Gunicorn (WSGI) | `def` | ✅ TAK | ✅ OK (WSGI normalnie) |
| FastAPI | Uvicorn (ASGI) | `async def` | ✅ TAK | ✅ Async I/O! |
| FastAPI | Uvicorn (ASGI) | `def` | ✅ TAK | ⚠️ Thread pool overhead |
| FastAPI | Gunicorn (WSGI) | `async def` | ❌ NIE | Gunicorn nie wspiera ASGI |

### Best practices:

```python
# ✅ DOBRZE - Django na ASGI z async
# settings.py
ASGI_APPLICATION = 'myproject.asgi.application'

# uruchom: uvicorn myproject.asgi:application
# views: async def dla I/O operations

# ✅ DOBRZE - FastAPI na ASGI z async
# uruchom: uvicorn main:app
# endpoints: async def dla I/O, def dla CPU-bound

# ❌ ŹLE - Django na WSGI z async views
# gunicorn myproject.wsgi:application
# views: async def ← BLOKUJE, brak korzyści!

# ⚠️ OK ALE NIEOPTYMALNE - FastAPI na ASGI z sync
# uvicorn main:app
# endpoints: def ← działa ale thread pool overhead
```

### Kiedy co używać:

**Django:**
- Async views + ASGI (Uvicorn) jeśli masz dużo I/O
- Sync views + WSGI (Gunicorn) jeśli podstawowa aplikacja

**FastAPI:**
- Zawsze ASGI (Uvicorn)
- `async def` dla endpoints z I/O (database, APIs)
- `def` dla prostych endpoints bez I/O (ale rzadko)

---

## 7. Gunicorn + Uvicorn workers vs czysty Uvicorn

**Pytanie:**
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```
Dlaczego tak, w czym to będzie lepsze niż:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Odpowiedź:**

Świetne pytanie! Oba podejścia działają, ale są **subtelne różnice**.

### Szybka odpowiedź:

**Dla produkcji FastAPI:**
- **Gunicorn + Uvicorn workers** ← RECOMMENDED (oficjalna rekomendacja FastAPI)
- **Czysty Uvicorn z --workers** ← też OK, ale mniej dojrzałe process management

### Szczegółowe porównanie:

#### Opcja 1: Gunicorn + Uvicorn workers (RECOMMENDED)

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

**Architektura:**
```
Gunicorn (master process)
  ├─ Uvicorn worker 1 (proces)
  ├─ Uvicorn worker 2 (proces)
  ├─ Uvicorn worker 3 (proces)
  └─ Uvicorn worker 4 (proces)
```

**Co daje Gunicorn:**
- ✅ **Dojrzały process manager** (od 2010, battle-tested)
- ✅ **Graceful restarts** (zero-downtime deployments)
- ✅ **Worker health monitoring** (auto-restart crashed workers)
- ✅ **Pre-fork model** (workers są fork'owane, nie spawn'owane) - *wyjaśnione poniżej*
- ✅ **Signal handling** (SIGHUP, SIGTERM, SIGINT, etc.)
- ✅ **Resource limits** per worker
- ✅ **Timeout configuration** (kill hanging workers)
- ✅ **Worker scaling** (dynamic worker count)
- ✅ **Logging** (access logs, error logs, formatting)

##### 🔍 Co to znaczy "fork" vs "spawn"?

**Fork (fork'owanie procesu):**
```python
# W Unix/Linux - fork() tworzy KOPIĘ procesu
import os

pid = os.fork()  # Tworzy kopię całego procesu
# Po fork():
# - Dziecko (child) dziedziczy pamięć rodzica (parent)
# - Dziecko ma TĘ SAMĄ pamięć (początkowo shared, copy-on-write)
# - Szybkie (bo nie kopiuje od razu wszystkiego)
```

**Spawn (spawn'owanie procesu):**
```python
# W Windows / multiprocessing.spawn - tworzy NOWY proces
import multiprocessing

# Tworzy zupełnie nowy proces od zera
# - Dziecko NIE dziedziczy pamięci rodzica
# - Musi załadować wszystko od nowa (Python interpreter, moduły, etc.)
# - Wolniejsze (bo wszystko od nowa)
```

**Pre-fork model w Gunicorn:**

```
1. Gunicorn master process startuje
   └─ Ładuje Twój kod (app = FastAPI())
   └─ Ładuje wszystkie biblioteki (FastAPI, Pydantic, SQLAlchemy, etc.)

2. Gunicorn fork'uje workers (np. 4 workery)
   ├─ Worker 1 (fork od mastera) ← SZYBKIE! (dziedziczy załadowany kod)
   ├─ Worker 2 (fork od mastera) ← SZYBKIE!
   ├─ Worker 3 (fork od mastera) ← SZYBKIE!
   └─ Worker 4 (fork od mastera) ← SZYBKIE!

Każdy worker:
✅ MA już załadowaną aplikację (skopiował z mastera)
✅ MA już załadowane biblioteki (skopiował z mastera)
✅ Startuje SZYBKO (bo nie musi ładować od nowa)
✅ Oszczędza pamięć (copy-on-write - dopóki nie modyfikuje, dzieli pamięć z masterem)
```

**Gdyby Gunicorn używał spawn (nie używa!):**
```
1. Gunicorn master process startuje

2. Gunicorn spawn'uje workers
   ├─ Worker 1 (nowy proces) ← WOLNE! (musi załadować wszystko od nowa)
   │   └─ Ładuje Python interpreter
   │   └─ Ładuje FastAPI, Pydantic, SQLAlchemy, etc.
   │   └─ Parsuje Twój kod
   │   └─ Tworzy app = FastAPI()
   │
   ├─ Worker 2 (nowy proces) ← WOLNE! (powtarza to samo)
   ├─ Worker 3 (nowy proces) ← WOLNE!
   └─ Worker 4 (nowy proces) ← WOLNE!

Każdy worker:
❌ Musi załadować wszystko od nowa
❌ Wolniejszy start
❌ Więcej pamięci (każdy ma swoją kopię wszystkiego)
```

**Dlaczego pre-fork model jest lepszy:**

1. **Szybki start workerów**
   - Fork jest szybki (kilka ms)
   - Spawn jest wolny (setki ms - musi załadować Python, biblioteki, kod)

2. **Mniejsze zużycie pamięci (copy-on-write)**
   ```
   Master załadował FastAPI (50 MB w pamięci)
   Worker 1 fork → początkowo dzieli te same 50 MB (COW)
   Worker 2 fork → początkowo dzieli te same 50 MB (COW)
   Worker 3 fork → początkowo dzieli te same 50 MB (COW)
   Worker 4 fork → początkowo dzieli te same 50 MB (COW)

   Tylko gdy worker MODYFIKUJE dane, robi swoją kopię (copy-on-write)
   Oszczędność pamięci = ogromna!
   ```

3. **Graceful restarts są szybsze**
   ```bash
   kill -HUP <gunicorn_pid>

   # Fork'owanie nowych workerów = szybkie (master ma załadowany kod)
   # Spawn'owanie = wolne (każdy worker ładowałby od nowa)
   ```

**Podsumowanie:**
- **Fork** = kopia procesu (szybkie, oszczędne, używane przez Gunicorn)
- **Spawn** = nowy proces (wolne, pamięciożerne, używane przez Windows/multiprocessing.spawn)
- **Pre-fork model** = workers są fork'owane przy starcie (nie przy każdym requeście!)

#### Opcja 2: Czysty Uvicorn z --workers

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Architektura:**
```
Uvicorn (master process)
  ├─ Uvicorn worker 1 (proces)
  ├─ Uvicorn worker 2 (proces)
  ├─ Uvicorn worker 3 (proces)
  └─ Uvicorn worker 4 (proces)
```

**Co daje Uvicorn:**
- ✅ **Działa** (basic process management)
- ⚠️ **Mniej dojrzały process manager** (Uvicorn fokusuje się na ASGI, nie process management)
- ⚠️ **Mniej opcji** (mniej flags niż Gunicorn)
- ⚠️ **Graceful restarts** - prostsze niż Gunicorn

### Praktyczne różnice:

#### 1. Graceful Restart (zero-downtime deployment)

**Gunicorn:**
```bash
# Deploy nowej wersji aplikacji bez downtime
kill -HUP <gunicorn_pid>

# Co się dzieje:
# 1. Gunicorn master dostaje SIGHUP
# 2. Master spawn'uje nowe workery (z nowym kodem)
# 3. Stare workery kończą obsługiwać istniejące requesty
# 4. Stare workery są kill'owane po zakończeniu requestów
# 5. Zero downtime!
```

**Uvicorn:**
```bash
# Uvicorn też obsługuje, ale prostsze
# Musisz sam zarządzać procesem
```

#### 2. Worker Timeout

**Gunicorn:**
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --timeout 30  # Kill worker jeśli request > 30 sec

# Chroni przed hanging requests!
```

**Uvicorn:**
```bash
uvicorn main:app --workers 4
# Brak built-in timeout dla workerów
# (można ustawić timeout w aplikacji)
```

#### 3. Logging i Monitoring

**Gunicorn:**
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --access-logfile /var/log/gunicorn/access.log \
  --error-logfile /var/log/gunicorn/error.log \
  --log-level info \
  --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s'

# Pełna kontrola nad logami!
```

**Uvicorn:**
```bash
uvicorn main:app --workers 4 --log-level info
# Prostsze opcje logowania
```

#### 4. Konfiguracja z pliku

**Gunicorn:**
```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 30
keepalive = 5
max_requests = 1000  # Restart worker co 1000 requests (memory leak protection)
max_requests_jitter = 50
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Użycie: gunicorn -c gunicorn.conf.py main:app
```

**Uvicorn:**
```bash
# Brak wbudowanego wsparcia dla pliku konfiguracyjnego
# Musisz używać flags lub environment variables
```

### Kiedy co używać?

#### Użyj Gunicorn + Uvicorn workers jeśli:
- ✅ Produkcja (production deployment)
- ✅ Potrzebujesz zero-downtime deployments
- ✅ Chcesz dojrzałe process management
- ✅ Potrzebujesz worker timeouts
- ✅ Chcesz advanced logging
- ✅ Chcesz konfigurację z pliku
- ⭐ **Oficjalna rekomendacja FastAPI**

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 30 \
  --graceful-timeout 30 \
  --keep-alive 5
```

#### Użyj czystego Uvicorn jeśli:
- ✅ Development/testing
- ✅ Prosta aplikacja (małe traffic)
- ✅ Nie potrzebujesz zaawansowanego process management
- ✅ Deployment w kontenerze (Docker) gdzie orchestrator (Kubernetes) zarządza procesami

```bash
# Development
uvicorn main:app --reload

# Production (Docker + Kubernetes)
uvicorn main:app --host 0.0.0.0 --port 8000
# Kubernetes zarządza replikami, health checks, restarts
```

### Rekomendacja FastAPI (oficjalna dokumentacja):

> **For production, use Gunicorn with Uvicorn workers:**
> ```bash
> gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
> ```

**Dlaczego?**
- Gunicorn = battle-tested process manager (10+ lat w produkcji)
- Uvicorn = nowoczesny ASGI server (szybki, async)
- **Best of both worlds!**

### Docker example:

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Production: Gunicorn + Uvicorn workers
CMD ["gunicorn", "main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "30", \
     "--graceful-timeout", "30"]
```

### Podsumowanie:

| Feature | Gunicorn + Uvicorn | Czysty Uvicorn |
|---------|-------------------|----------------|
| Process management | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Graceful restarts | ✅ Advanced | ✅ Basic |
| Worker timeouts | ✅ Built-in | ❌ Musisz sam |
| Logging | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Config file | ✅ Python file | ❌ Tylko flags |
| Zero-downtime deploy | ✅ SIGHUP | ⚠️ Możliwe ale trudniejsze |
| Battle-tested | ✅ 10+ lat | ⚠️ Nowsze (process mgmt) |
| FastAPI recommendation | ✅ TAK | ⚠️ OK dla Docker |

**Wniosek:** Użyj **Gunicorn + Uvicorn workers** dla produkcji (poza Kubernetes).

---

## 8. Workers - proces vs wątek

**Pytanie:** `(2 × liczba CPU cores) + 1` - czy każdy worker to zawsze oddzielny proces (nie wątek)?

**Odpowiedź:**

### Szybka odpowiedź:

**TAK**, worker to **zawsze oddzielny proces** (nie wątek).

**Dlaczego proces a nie wątek?**

**Python GIL** (Global Interpreter Lock) - wątki w Pythonie nie mogą wykonywać kodu jednocześnie na różnych cores!

### Szczegóły:

#### Problem: Python GIL

```python
# GIL = Global Interpreter Lock
# Tylko JEDEN wątek może wykonywać Python bytecode jednocześnie

# Przykład - 2 wątki, 2 CPU cores:
Thread 1 (CPU 1): wykonuje Python kod
Thread 2 (CPU 2): CZEKA na GIL (nie może wykonywać kodu!)

# Efekt: threading w Pythonie NIE daje performance boost dla CPU-bound code
```

**Dlatego używamy PROCESÓW, nie WĄTKÓW:**

```python
# PROCESY - każdy ma własny GIL
Process 1 (CPU 1): wykonuje Python kod - własny GIL
Process 2 (CPU 2): wykonuje Python kod - własny GIL

# Efekt: prawdziwy paralelizm!
```

### Gunicorn - zawsze procesy

```bash
gunicorn main:app --workers 4

# Tworzy:
Master process (PID 1000)
  ├─ Worker process 1 (PID 1001) - własny GIL
  ├─ Worker process 2 (PID 1002) - własny GIL
  ├─ Worker process 3 (PID 1003) - własny GIL
  └─ Worker process 4 (PID 1004) - własny GIL
```

**Weryfikacja:**
```bash
ps aux | grep gunicorn

# Output:
# user 1000 ... gunicorn: master [main:app]
# user 1001 ... gunicorn: worker [main:app]
# user 1002 ... gunicorn: worker [main:app]
# user 1003 ... gunicorn: worker [main:app]
# user 1004 ... gunicorn: worker [main:app]

# 5 procesów (1 master + 4 workers)
```

#### 🔍 Jaka jest rola master procesu?

**TAK**, master ma **zupełnie inne zadania** niż workers!

**Master NIE obsługuje requestów** - to robią tylko workers.

**Zadania master procesu:**

1. **Process Management**
   ```python
   # Master fork'uje workers przy starcie
   Master process startuje
     ↓
   Fork worker 1, worker 2, worker 3, worker 4
     ↓
   Master czeka i monitoruje workers
   ```

2. **Health Monitoring**
   ```
   Worker 2 crash! (exit code 1)
     ↓
   Master wykrywa (SIGCHLD signal)
     ↓
   Master fork'uje nowy worker 2
     ↓
   System działa dalej (auto-healing!)
   ```

3. **Signal Handling**
   ```bash
   kill -HUP <master_pid>  # Graceful restart
     ↓
   Master dostaje SIGHUP
     ↓
   Master fork'uje NOWE workery (z nowym kodem)
     ↓
   Master czeka aż STARE workery kończą requesty
     ↓
   Master kill'uje stare workery
     ↓
   Zero downtime deployment! ✅
   ```

   ```bash
   kill -TERM <master_pid>  # Graceful shutdown
     ↓
   Master wysyła SIGTERM do wszystkich workerów
     ↓
   Workers kończą istniejące requesty
     ↓
   Workers się wyłączają
     ↓
   Master się wyłącza
   ```

4. **Load Balancing (ale NIE jak myślisz!)**

   **WAŻNE:** Master **NIE robi** tradycyjnego load balancingu (round-robin)!

   **Gunicorn używa "shared socket" model:**

   ```
   Master tworzy listening socket (port 8000)
     ↓
   Master fork'uje workers (każdy dziedziczy socket)
     ↓
   Każdy worker DZIELI ten sam socket (shared)
     ↓
   Workers rywalizują o requesty (whoever accepts first)
   ```

   **Jak to działa:**
   ```python
   # Uproszczona wizualizacja

   Master: socket = bind(8000)  # Tworzy socket
   Master: fork() → Worker 1, Worker 2, Worker 3, Worker 4

   # Każdy worker:
   while True:
       client = socket.accept()  # Czeka na request
       # ^^ Kernel wybiera który worker dostanie request!
       handle_request(client)
   ```

   **Request przychodzi:**
   ```
   Request → Port 8000 (shared socket)
     ↓
   Kernel widzi: 4 workery czekają na accept()
     ↓
   Kernel wybiera worker który dostanie request (kernel load balancing)
     ↓
   Worker 2 dostaje request (bo był dostępny pierwszy)
     ↓
   Worker 2 obsługuje request
     ↓
   Worker 2 wraca do accept() (czeka na następny)
   ```

   **To NIE jest round-robin!**
   - ❌ Master NIE przekazuje requestów po kolei
   - ❌ Master NIE decyduje który worker dostaje request
   - ✅ **Kernel decyduje** (whoever is ready first)
   - ✅ Nazywa się: **kernel load balancing** / **thundering herd**

5. **Worker Configuration & Limits**
   ```python
   # Master śledzi każdego workera:
   Worker 1: 300 requests obsłużonych
   Worker 2: 450 requests obsłużonych (bliski max_requests!)
   Worker 3: 100 requests obsłużonych
   Worker 4: 200 requests obsłużonych

   # Gdy worker osiągnie limit:
   Worker 2: 1000 requests → RESTART (memory leak protection)
   ```

**Podsumowanie - Master vs Workers:**

| Rola | Master | Workers |
|------|--------|---------|
| **Obsługuje requesty** | ❌ NIE | ✅ TAK |
| **Fork'uje procesów** | ✅ TAK | ❌ NIE |
| **Monitoruje health** | ✅ TAK | ❌ NIE |
| **Przyjmuje sygnały (SIGHUP)** | ✅ TAK | ❌ NIE |
| **Graceful restart** | ✅ TAK (koordynuje) | Workers się restartują |
| **Load balancing** | ❌ NIE (kernel!) | Workers rywalizują |

---

#### 🔄 Gunicorn "load balancing" vs nginx load balancing

**To są RÓŻNE warstwy!**

**Gunicorn master:**
```
Gunicorn master (NIE balansuje sam!)
  ↓ (shared socket - kernel balancing)
├─ Worker 1 (rywalizuje o requesty)
├─ Worker 2 (rywalizuje o requesty)
├─ Worker 3 (rywalizuje o requesty)
└─ Worker 4 (rywalizuje o requesty)

- Master NIE przekazuje requestów
- Kernel wybiera który worker dostaje request
- Workers dzielą ten sam socket
- "Thundering herd" + kernel scheduling
```

**nginx load balancer:**
```
nginx (AKTYWNIE balansuje - round-robin/least_conn/ip_hash)
  ↓ (proxy_pass)
├─ Gunicorn instance 1 (127.0.0.1:8001) → 4 workers
├─ Gunicorn instance 2 (127.0.0.1:8002) → 4 workers
└─ Gunicorn instance 3 (127.0.0.1:8003) → 4 workers

- nginx AKTYWNIE wybiera backend
- nginx używa round-robin (default) lub least_conn
- To jest tradycyjny load balancer
```

**Przykład konfiguracji:**

```nginx
# nginx.conf
upstream gunicorn_backends {
    # Load balancing algorithm (pick one):

    # 1. Round-robin (default)
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;

    # 2. Least connections (lepsze dla uneven loads)
    # least_conn;
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
    # server 127.0.0.1:8003;

    # 3. IP hash (sticky sessions)
    # ip_hash;
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
    # server 127.0.0.1:8003;
}

server {
    listen 80;

    location / {
        proxy_pass http://gunicorn_backends;  # nginx balansuje!
    }
}
```

**Flow kompletny:**

```
Request przychodzi
  ↓
nginx (load balancer - round-robin)
  ↓ wybiera
Gunicorn instance 2 (127.0.0.1:8002)
  ↓ (shared socket - kernel balancing)
Kernel wybiera
  ↓
Worker 3 (w Gunicorn instance 2)
  ↓
FastAPI obsługuje request
```

**Dwie warstwy load balancingu:**
1. **nginx** → balansuje między **Gunicorn instances** (inter-instance)
2. **Gunicorn master/kernel** → balansuje między **workers** (intra-instance)

---

#### 📊 Czy zamiast Gunicorn użyć tylko load balancera?

**NIE!** To są **różne warstwy** - potrzebujesz **OBIE**!

**nginx = HTTP Server + Reverse Proxy + Load Balancer**
- Serwuje static files
- Terminuje SSL
- Balansuje między SERWERAMI/INSTANCJAMI
- NIE URUCHAMIA Pythona!

**Gunicorn = WSGI Server + Process Manager**
- Uruchamia Python kod
- Zarządza worker processes
- Health monitoring (auto-restart)
- Graceful restarts
- NIE JEST HTTP serverem (choć przyjmuje HTTP)

**Nie możesz zastąpić jednego drugim!**

**Setup 1: Tylko Gunicorn (bez nginx)**
```bash
gunicorn main:app --bind 0.0.0.0:80 --workers 4

❌ Problemy:
- Brak SSL termination (musisz robić w Pythonie - wolniejsze)
- Brak static files serving (Python serwuje - wolne)
- Brak load balancing między serwerami
- Brak security features (rate limiting, etc.)
- Gunicorn wystawiony bezpośrednio na internet (ryzyko)
```

**Setup 2: Tylko nginx (bez Gunicorn)**
```nginx
server {
    location / {
        # nginx nie może uruchomić Pythona!
        # ❌ Nie ma jak uruchomić FastAPI
    }
}
```

**Setup 3: nginx + Gunicorn (RECOMMENDED)**
```
nginx (port 80/443)
  ↓ proxy_pass
Gunicorn (port 8000, localhost only)
  ↓ workers
FastAPI

✅ Best of both worlds:
- nginx: SSL, static files, security, load balancing
- Gunicorn: Python execution, process management, graceful restarts
```

---

#### 🎯 Kiedy używać nginx load balancingu vs Gunicorn workers?

**1 serwer:**
```
nginx (reverse proxy - NIE load balancing)
  ↓ proxy_pass http://127.0.0.1:8000
Gunicorn master (1 instance)
  ├─ Worker 1
  ├─ Worker 2
  ├─ Worker 3
  └─ Worker 4

- Tylko kernel balancing (między workers)
- nginx NIE balansuje (bo tylko 1 backend)
```

**Multiple serwery (horizontal scaling):**
```
nginx (load balancer - round-robin)
  ├─ proxy_pass → Server 1 (Gunicorn + 4 workers)
  ├─ proxy_pass → Server 2 (Gunicorn + 4 workers)
  └─ proxy_pass → Server 3 (Gunicorn + 4 workers)

- nginx balansuje między SERWERAMI
- Kernel balansuje między WORKERS (w każdym serwerze)
- Razem: 12 workers (3 × 4)
```

**Docker Compose (multiple containers):**
```yaml
# docker-compose.yml
services:
  nginx:
    image: nginx

  web_1:
    build: .
    command: gunicorn main:app --workers 4 --bind 0.0.0.0:8000

  web_2:
    build: .
    command: gunicorn main:app --workers 4 --bind 0.0.0.0:8000

  web_3:
    build: .
    command: gunicorn main:app --workers 4 --bind 0.0.0.0:8000
```

```nginx
# nginx.conf
upstream web_backends {
    server web_1:8000;
    server web_2:8000;
    server web_3:8000;
}

server {
    location / {
        proxy_pass http://web_backends;
    }
}
```

Teraz masz **3 Gunicorn instances × 4 workers = 12 workers total**
- nginx balansuje między 3 containers
- Kernel balansuje między 4 workers (w każdym containerze)

---

#### 🔑 Key Takeaways

1. **Master process = Process Manager, NIE load balancer**
   - Fork'uje workers
   - Monitoruje health
   - Obsługuje signals (SIGHUP, SIGTERM)
   - NIE przekazuje requestów (to robi kernel!)

2. **Load balancing w Gunicorn = Kernel scheduling**
   - Shared socket między workers
   - Kernel decyduje który worker dostaje request
   - NIE round-robin (whoever is ready first)
   - Nazywa się: **thundering herd** / **kernel load balancing**

3. **Gunicorn vs nginx - różne warstwy!**
   - nginx = HTTP server, reverse proxy, load balancer (między instancjami)
   - Gunicorn = WSGI server, process manager (między workers)
   - Potrzebujesz OBIE warstwy w produkcji

4. **Load balancing architecture:**
   ```
   nginx (load balancer)          ← Warstwa 1: między serwerami
     ↓
   Gunicorn master (shared socket) ← Warstwa 2: między workers (kernel)
     ↓
   Workers
   ```

### Uvicorn - też procesy

```bash
uvicorn main:app --workers 4

# Tworzy:
Master process (PID 2000)
  ├─ Worker process 1 (PID 2001)
  ├─ Worker process 2 (PID 2002)
  ├─ Worker process 3 (PID 2003)
  └─ Worker process 4 (PID 2004)
```

### Dlaczego (2 × CPU cores) + 1?

**Formula:** `workers = (2 × CPU_cores) + 1`

**Przykład:**
- 4 CPU cores → `(2 × 4) + 1 = 9 workers`

**Dlaczego 2×?**

```
CPU-bound work: 1 worker per core (1×)
  - Jeśli tylko obliczenia, 1 worker per core wystarczy

I/O-bound work: 2+ workers per core (2×+)
  - Worker czeka na I/O (database, API calls)
  - Podczas czekania, CPU jest wolny
  - Inny worker może używać CPU
  - Więcej workerów = lepsze wykorzystanie CPU podczas I/O waits
```

**Dlaczego +1?**

```
+1 = buffer dla "spare capacity"
  - Jeden worker jako backup
  - Jeśli jeden worker się crashuje, masz zapas
  - Statystyczne rozprowadzenie load
```

### Procesy vs Wątki - podsumowanie:

| | Procesy | Wątki |
|---|---------|-------|
| **GIL** | Każdy proces ma własny GIL | Wszystkie wątki dzielą jeden GIL |
| **Paralelizm** | ✅ Prawdziwy (multi-core) | ❌ Nie dla CPU-bound (GIL!) |
| **Memory** | Każdy proces ma własną pamięć | Wątki dzielą pamięć |
| **Izolacja** | ✅ Pełna (crash jednego nie wpływa na inne) | ❌ Słaba (crash może zabić process) |
| **Overhead** | Większy (każdy proces = cały Python interpreter) | Mniejszy |
| **Use case** | Web servers (Gunicorn, Uvicorn) | Async I/O w obrębie procesu |

### Kiedy PROCESY (Gunicorn workers):

```python
# Web server - wiele requestów jednocześnie
gunicorn main:app --workers 4  # 4 procesy

# Każdy request może być obsłużony przez inny proces
# Request 1 → Worker process 1 (CPU 1)
# Request 2 → Worker process 2 (CPU 2)
# Request 3 → Worker process 3 (CPU 3)
# Request 4 → Worker process 4 (CPU 4)

# Prawdziwy paralelizm!
```

### Kiedy WĄTKI (w obrębie workera):

```python
# Uvicorn worker używa wątków WEWNĘTRZNIE dla async I/O
# ALE to nie są Python wątki wykonujące kod aplikacji!

# Uvicorn worker (1 proces):
#   - event loop (asyncio)
#   - thread pool dla sync operations (np. file I/O)
#   - async tasks (nie blokują się dzięki await, nie GIL!)

# Async = nie używa wielu wątków dla kodu aplikacji
# Async = event loop + cooperative multitasking
```

### Async vs Multi-process:

```python
# Multi-process (Gunicorn - 4 workers):
# 4 procesy × 1 request jednocześnie = 4 requests jednocześnie
# Koszt: 4× Python interpreter (RAM: ~200MB × 4 = 800MB)

# Async (Uvicorn - 1 worker):
# 1 proces × 1000 concurrent requests (async I/O)
# Koszt: 1× Python interpreter (RAM: ~200MB)

# Best of both worlds (Gunicorn + Uvicorn workers):
# 4 procesy × 1000 concurrent requests każdy = 4000 requests jednocześnie!
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Memory consumption:

```bash
# Test: FastAPI app
# 1 worker:
ps aux | grep uvicorn
# RAM: ~200MB (baseline)

# 4 workers:
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
# RAM: ~800MB (4 × 200MB)

# Każdy worker = osobny proces = osobna kopia interpretera!
```

### Podsumowanie:

**TAK, worker to zawsze proces (nie wątek)!**

**Dlaczego?**
- Python GIL uniemożliwia prawdziwy paralelizm w wątkach
- Procesy mają własny GIL każdy
- Procesy mogą używać wielu CPU cores jednocześnie

**Formula workerów:**
```python
import multiprocessing

# Formula:
workers = (2 × multiprocessing.cpu_count()) + 1

# 4 cores → 9 workers
# 8 cores → 17 workers
```

**Wątki są używane:**
- Wewnątrz Uvicorn workera (dla async I/O thread pool)
- ALE nie dla obsługi requestów aplikacji (to robi event loop + async)

---

## 9. nginx - static files configuration

**Pytanie:** nginx automatycznie rozpoznaje statyczne pliki, czy to się konfiguruje w nim co jest statyczne?

**Odpowiedź:**

### Szybka odpowiedź:

**Musisz SKONFIGUROWAĆ** w nginx co jest statyczne. nginx **nie rozpoznaje automatycznie** plików statycznych.

### Dlaczego?

nginx to HTTP server - nie wie co jest w Twojej aplikacji. Musisz mu powiedzieć:
- Gdzie są pliki statyczne (ścieżka na dysku)
- Które URL-e mają serwować static files
- Które URL-e mają być proxy'owane do aplikacji

### Przykład konfiguracji:

```nginx
# /etc/nginx/sites-available/myapp

server {
    listen 80;
    server_name example.com;

    # 1. STATIC FILES - nginx serwuje z dysku
    location /static/ {
        alias /var/www/myapp/static/;  # Ścieżka na dysku
        expires 30d;  # Cache na 30 dni
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/myapp/media/;  # Uploaded files
        expires 7d;
    }

    # 2. API/DYNAMIC - proxy do aplikacji (Uvicorn/Gunicorn)
    location / {
        proxy_pass http://127.0.0.1:8000;  # Przekazuje do Pythona
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Jak to działa:

```
Request: GET /static/style.css
  ↓
nginx sprawdza: location /static/ {...}
  ↓
Pasuje! nginx czyta z dysku: /var/www/myapp/static/style.css
  ↓
Zwraca plik bezpośrednio (NIE wywołuje Pythona)

---

Request: GET /api/users
  ↓
nginx sprawdza: location /api/ {...} - nie ma takiej
  ↓
nginx sprawdza: location / {...} - PASUJE (fallback)
  ↓
Proxy do http://127.0.0.1:8000/api/users
  ↓
Gunicorn/Uvicorn obsługuje request
```

### Szczegóły konfiguracji:

#### 1. `location` directive - kolejność ma znaczenie!

```nginx
server {
    # nginx dopasowuje location w kolejności:
    # 1. Exact match (=)
    # 2. Prefix match (^~)
    # 3. Regex match (~)
    # 4. Prefix match (bez modyfikatora)

    # Exact match - najwyższy priorytet
    location = /favicon.ico {
        alias /var/www/myapp/static/favicon.ico;
    }

    # Prefix match z ^~ - blokuje regex matching
    location ^~ /static/ {
        alias /var/www/myapp/static/;
    }

    # Regex match - case sensitive
    location ~ \.(jpg|jpeg|png|gif|ico)$ {
        alias /var/www/myapp/images/;
    }

    # Regex match - case insensitive
    location ~* \.(jpg|jpeg|png|gif|ico)$ {
        alias /var/www/myapp/images/;
    }

    # Prefix match (fallback)
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

#### 2. `alias` vs `root`

```nginx
# ALIAS - zamienia prefix w URL na ścieżkę
location /static/ {
    alias /var/www/myapp/static/;
}
# URL: /static/style.css
# File: /var/www/myapp/static/style.css  (prefix usunięty!)

# ROOT - dodaje URL do root path
location /static/ {
    root /var/www/myapp;
}
# URL: /static/style.css
# File: /var/www/myapp/static/style.css  (prefix zachowany!)
```

**Kiedy co?**

```nginx
# ALIAS - gdy struktura URL ≠ struktura dysku
location /static/ {
    alias /var/www/myapp/staticfiles/;  # Inna nazwa folderu
}

# ROOT - gdy struktura URL = struktura dysku
location /static/ {
    root /var/www/myapp;  # /var/www/myapp/static/ na dysku
}
```

#### 3. Django example (collectstatic):

```python
# Django settings.py
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/myapp/staticfiles/'  # Gdzie collectstatic zapisuje

# Komenda:
python manage.py collectstatic
# Kopiuje pliki z apps do /var/www/myapp/staticfiles/
```

```nginx
# nginx config
location /static/ {
    alias /var/www/myapp/staticfiles/;  # Gdzie Django zapisał pliki
    expires 30d;
}
```

#### 4. FastAPI example:

```python
# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount static files (dla development)
app.mount("/static", StaticFiles(directory="static"), name="static")
```

**Development (bez nginx):**
```bash
uvicorn main:app --reload
# http://localhost:8000/static/style.css
# FastAPI serwuje static files
```

**Production (z nginx):**
```nginx
# nginx serwuje static files (szybciej niż Python!)
location /static/ {
    alias /var/www/myapp/static/;
}

# Python obsługuje tylko API
location / {
    proxy_pass http://127.0.0.1:8000;
}
```

```python
# main.py (production)
app = FastAPI()
# NIE montuj static files - nginx serwuje!
# app.mount("/static", ...)  ← Usuń to dla produkcji
```

### Automatyczne rozpoznawanie? NIE!

**Dlaczego nginx nie może automatycznie rozpoznać static files?**

```
nginx nie wie:
- Gdzie są pliki (ścieżka na dysku)
- Które URL-e mają być static (może /images to API endpoint?)
- Jakie extensions są static (może .json to API response?)

Dlatego MUSISZ skonfigurować ręcznie!
```

### Najlepsze praktyki:

```nginx
server {
    listen 80;
    server_name example.com;

    # Root directory (dla root directive)
    root /var/www/myapp;

    # 1. Favicon (exact match - najszybsze)
    location = /favicon.ico {
        alias /var/www/myapp/static/favicon.ico;
        access_log off;  # Nie loguj favicon requests
    }

    # 2. Static files (CSS, JS, images)
    location /static/ {
        alias /var/www/myapp/staticfiles/;
        expires 30d;  # Browser cache 30 dni
        add_header Cache-Control "public, immutable";
        access_log off;  # Nie loguj static files (performance)
    }

    # 3. Media files (user uploads)
    location /media/ {
        alias /var/www/myapp/media/;
        expires 7d;  # Krótszy cache (content się zmienia)
    }

    # 4. API/Dynamic content (fallback - wszystko inne)
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### Weryfikacja:

```bash
# 1. Test konfiguracji
sudo nginx -t

# 2. Reload nginx
sudo systemctl reload nginx

# 3. Test static file
curl -I http://example.com/static/style.css
# HTTP/1.1 200 OK
# Server: nginx
# X-Served-By: nginx (nie Python!)

# 4. Test API
curl -I http://example.com/api/users
# HTTP/1.1 200 OK
# (proxy'owane do Pythona)
```

### Podsumowanie:

❌ **nginx NIE rozpoznaje automatycznie static files**
✅ **Musisz skonfigurować:**
  - `location /static/` - które URL-e
  - `alias /path/to/static/` - gdzie pliki na dysku
  - `expires 30d` - jak długo cache'ować

**Dlaczego konfiguracja ręczna?**
- nginx nie wie gdzie są Twoje pliki
- nginx nie wie które URL-e to API a które static files
- Dajesz pełną kontrolę (security, performance)

---

## 10. Proxy vs Reverse Proxy

**Pytanie:** nginx nazywane jest reverse proxy, dlaczego, tzn. dlaczego nie proxy? Czym różni się proxy od reverse proxy?

**Odpowiedź:**

Świetne pytanie! To jedno z najczęściej mylonych pojęć.

### Szybka odpowiedź:

- **Proxy (Forward Proxy)** - działa **po stronie klienta** (ukrywa klientów)
- **Reverse Proxy** - działa **po stronie serwera** (ukrywa serwery)

**nginx = Reverse Proxy** (po stronie serwera)

### Szczegóły:

#### 1. Forward Proxy (po prostu "Proxy")

**Kto używa:** Klient konfiguruje proxy

**Cel:** Ukryć tożsamość klienta, obejść blokady, cache

```
Client 1 ────┐
             │
Client 2 ────┼──→ [PROXY] ────→ Internet (example.com)
             │
Client 3 ────┘

- Klienci WIEDZĄ o proxy (muszą go skonfigurować)
- Serwer (example.com) WIDZI tylko IP proxy (nie wie o klientach)
- Proxy chroni/ukrywa KLIENTÓW
```

**Przykład:** VPN, corporate proxy, Squid

**Use cases:**
- Przeglądanie internetu przez VPN (ukrycie IP)
- Obejście geo-blocking (VPN → zmiana kraju)
- Corporate network (wszystkie requesty przez corporate proxy)
- Caching (proxy cache'uje popularne strony)

**Konfiguracja (po stronie klienta):**
```bash
# Browser settings:
Proxy: proxy.company.com:8080

# Lub environment variable:
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

**Request flow:**
```
curl http://example.com
  ↓
Klient wie: "mam proxy proxy.company.com:8080"
  ↓
Klient łączy się z proxy.company.com:8080
  ↓
Proxy łączy się z example.com (w imieniu klienta)
  ↓
example.com widzi IP: proxy.company.com (nie klienta!)
```

#### 2. Reverse Proxy

**Kto używa:** Serwer konfiguruje reverse proxy

**Cel:** Ukryć backend servers, load balancing, SSL termination

```
Client (internet)
  ↓
[REVERSE PROXY] (nginx)
  ↓
  ├──→ Backend Server 1
  ├──→ Backend Server 2
  └──→ Backend Server 3

- Klient NIE WIE o reverse proxy (transparentne)
- Klient myśli że mówi z example.com
- Reverse proxy UKRYWA backend servers
- Reverse proxy chroni SERWERY
```

**Przykład:** nginx, HAProxy, Traefik, Cloudflare

**Use cases:**
- Load balancing (rozprowadzenie traffic na wiele serwerów)
- SSL termination (nginx obsługuje HTTPS, backend plain HTTP)
- Caching (nginx cache'uje responses)
- Security (ukrycie struktury backend)
- Serwowanie static files (nginx zamiast Pythona)

**Konfiguracja (po stronie serwera):**
```nginx
# /etc/nginx/sites-available/myapp
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;  # Backend (Gunicorn)
    }
}
```

**Request flow:**
```
curl http://example.com
  ↓
DNS: example.com → 1.2.3.4 (nginx IP)
  ↓
Klient łączy się z 1.2.3.4:80 (nginx)
  ↓
nginx proxy_pass → 127.0.0.1:8000 (Gunicorn)
  ↓
Gunicorn obsługuje request
  ↓
Response: Gunicorn → nginx → Klient

Klient NIE WIE że backend to 127.0.0.1:8000 (widzi tylko nginx)
```

### Porównanie:

| | Forward Proxy | Reverse Proxy |
|---|---------------|---------------|
| **Strona** | Klient | Serwer |
| **Konfiguracja** | Klient musi skonfigurować | Transparentne dla klienta |
| **Ukrywa** | Klientów | Serwery |
| **Cel** | Ukryć IP klienta, obejść blokady | Load balancing, SSL, security |
| **Przykład** | VPN, Squid | nginx, HAProxy |
| **Klient wie?** | ✅ TAK (musi skonfigurować) | ❌ NIE (transparentne) |
| **Serwer wie?** | ❌ NIE (widzi tylko proxy IP) | ✅ TAK (konfiguruje reverse proxy) |

### Wizualizacja:

#### Forward Proxy:
```
[Client] ──konfiguruje──→ [Proxy] ──ukrywa klienta──→ [Server]
   ↑                         ↓
   └──────── nie widzi IP ───┘
```

#### Reverse Proxy:
```
[Client] ──nie wie o proxy──→ [Reverse Proxy] ──konfiguruje──→ [Backend]
                                     ↓                             ↑
                                     └────── ukrywa backend ───────┘
```

### Przykład praktyczny:

#### Forward Proxy (VPN):

```bash
# Bez VPN:
curl http://example.com
# example.com widzi: Twoje IP (1.2.3.4)

# Z VPN (forward proxy):
# 1. Konfigurujesz VPN na swoim komputerze
# 2. Cały traffic idzie przez VPN
curl http://example.com
# example.com widzi: VPN IP (5.6.7.8), nie Twoje IP!

# Klient (Ty):
- Wiesz że używasz VPN
- Musisz skonfigurować VPN

# Server (example.com):
- Nie wie że używasz VPN
- Widzi tylko IP VPN servera
```

#### Reverse Proxy (nginx):

```bash
# Klient:
curl http://example.com

# Klient:
- NIE WIE że za example.com jest nginx → Gunicorn
- Myśli że mówi bezpośrednio z example.com

# Serwer (administrator):
- Skonfigurował nginx jako reverse proxy
- nginx ukrywa backend (Gunicorn na porcie 8000)
- Klient nigdy nie widzi portu 8000

# Backend (Gunicorn):
- Działa na 127.0.0.1:8000 (localhost only!)
- Niedostępny z internetu (tylko przez nginx)
```

### Dlaczego "reverse"?

**Forward Proxy:**
- Request flow: Client → Proxy → Server (**forward** - w przód)
- Proxy po stronie klienta (na "początku" komunikacji)

**Reverse Proxy:**
- Request flow: Client → Reverse Proxy → Server (**reverse** - "odwrotnie", po stronie serwera)
- Proxy po stronie serwera (na "końcu" komunikacji)

**"Reverse" = odwrotny kierunek (po stronie serwera zamiast klienta)**

### nginx - Reverse Proxy Example:

```nginx
# nginx.conf
upstream backend {
    server 127.0.0.1:8001;  # Gunicorn worker 1
    server 127.0.0.1:8002;  # Gunicorn worker 2
    server 127.0.0.1:8003;  # Gunicorn worker 3
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://backend;  # Load balance między 3 workers

        # Headers (przekazuje info o kliencie do backendu)
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Klient:**
```bash
curl http://example.com/api/users

# Klient widzi:
- Host: example.com
- Port: 80
- Nie wie o 127.0.0.1:8001/8002/8003
```

**Backend (Gunicorn):**
```python
# FastAPI
@app.get("/api/users")
def get_users(request: Request):
    # request.client.host → IP klienta (z X-Real-IP header)
    # NIE 127.0.0.1 (bo nginx przekazuje X-Real-IP)
    print(request.headers['x-real-ip'])  # Real client IP
```

### Podsumowanie:

| Termin | Strona | Ukrywa | Klient wie? | Przykład |
|--------|--------|--------|-------------|----------|
| **Forward Proxy** | Klient | Klientów | ✅ TAK | VPN, Squid |
| **Reverse Proxy** | Serwer | Serwery | ❌ NIE | nginx, HAProxy |

**nginx = Reverse Proxy** bo:
- Działa po stronie serwera
- Ukrywa backend servers
- Klient nie wie o jego istnieniu (transparentne)
- Cel: load balancing, SSL, security, static files

---

## 11. gzip compression - jak klient wie że musi rozpakować?

**Pytanie:** Jeżeli nginx robi gzip compression to skąd klient wie, że trzeba response rozpakować i skąd wie jak to zrobić?

**Odpowiedź:**

Świetne pytanie! To działa przez **HTTP headers**.

### Szybka odpowiedź:

**HTTP header:** `Content-Encoding: gzip`

Klient (browser, curl) widzi ten header i automatycznie rozpakuje response.

### Szczegóły:

#### 1. Request (klient → serwer):

```http
GET /api/users HTTP/1.1
Host: example.com
Accept-Encoding: gzip, deflate, br
```

**`Accept-Encoding: gzip, deflate, br`** = "Klient mówi: umiem rozpakować gzip, deflate, brotli"

#### 2. Response (serwer → klient):

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Encoding: gzip
Content-Length: 1234

[skompresowane dane w gzip]
```

**`Content-Encoding: gzip`** = "Serwer mówi: response jest gzip-owany, rozpakuj"

#### 3. Klient (browser):

```
Browser widzi: Content-Encoding: gzip
  ↓
Browser automatycznie:
  1. Rozpakowuje gzip
  2. Parsuje JSON
  3. Wyświetla dane
```

**Użytkownik NIE WIDZI że było gzip!** (automatyczne)

### nginx konfiguracja:

```nginx
# /etc/nginx/nginx.conf

http {
    # Włącz gzip
    gzip on;

    # Minimalna wielkość response do kompresji (bajty)
    gzip_min_length 1000;  # Nie kompresuj małych responses (<1KB)

    # Typy MIME do kompresji
    gzip_types
        text/plain
        text/css
        application/json
        application/javascript
        text/xml
        application/xml
        application/xml+rss
        text/javascript;

    # Poziom kompresji (1-9, default: 6)
    gzip_comp_level 6;  # 1=szybko/słaba kompresja, 9=wolno/silna kompresja

    # Proxy support
    gzip_proxied any;  # Kompresuj nawet dla proxy requests

    # Vary header (ważne dla cache)
    gzip_vary on;
}
```

### Przykład (curl):

#### Bez gzip:

```bash
curl -v http://example.com/api/users

# Request:
> GET /api/users HTTP/1.1
> Host: example.com
# (brak Accept-Encoding)

# Response:
< HTTP/1.1 200 OK
< Content-Type: application/json
< Content-Length: 5000
# (brak Content-Encoding)

[{"id": 1, "name": "John"}, ...]  # 5000 bajtów
```

#### Z gzip:

```bash
curl -v -H "Accept-Encoding: gzip" http://example.com/api/users

# Request:
> GET /api/users HTTP/1.1
> Host: example.com
> Accept-Encoding: gzip

# Response:
< HTTP/1.1 200 OK
< Content-Type: application/json
< Content-Encoding: gzip       ← KLIENT WIDZI TEN HEADER
< Content-Length: 1200         ← Skompresowane (5000 → 1200!)
< Vary: Accept-Encoding        ← Cache hint

[binary gzip data]  # 1200 bajtów (zamiast 5000)
```

**curl automatycznie rozpakuje** jeśli widzi `Content-Encoding: gzip`.

---

### 🔧 curl i gzip compression - szczegóły

**TAK, curl automatycznie radzi sobie z gzip!**

#### Opcja 1: `--compressed` flag (RECOMMENDED - najłatwiejsze)

```bash
# --compressed automatycznie:
# 1. Wysyła Accept-Encoding: gzip, deflate
# 2. Rozpakowuje response automatycznie

curl --compressed http://example.com/api/users

# To jest NAJŁATWIEJSZY sposób!
# Nie musisz ręcznie dodawać headerów
```

**Co robi `--compressed`:**
```
Request:
  → Automatycznie dodaje: Accept-Encoding: gzip, deflate

Response (jeśli serwer kompresuje):
  ← Content-Encoding: gzip
  ← [binary gzip data]

curl automatycznie:
  → Widzi Content-Encoding: gzip
  → Rozpakowuje
  → Wyświetla zdekompresowane dane

Output:
  [{"id": 1, "name": "John"}, ...]  ✅ Rozpakowane!
```

#### Opcja 2: Ręczny header `Accept-Encoding`

```bash
# Ręcznie wysyłasz Accept-Encoding
curl -H "Accept-Encoding: gzip" http://example.com/api/users

# curl NADAL automatycznie rozpakuje!
# Output: [{"id": 1, "name": "John"}, ...]  ✅ Rozpakowane!
```

#### Opcja 3: Raw gzip (jeśli chcesz zobaczyć skompresowane dane)

```bash
# Zapisz skompresowane dane do pliku
curl -H "Accept-Encoding: gzip" --output compressed.gz http://example.com/api/users

# Sprawdź typ pliku
file compressed.gz
# Output: compressed.gz: gzip compressed data

# Rozpakuj ręcznie
gunzip compressed.gz
cat compressed
# Output: [{"id": 1, "name": "John"}, ...]
```

#### Porównanie rozmiaru (z --compressed vs bez)

```bash
# BEZ kompresji
curl -v http://example.com/api/users 2>&1 | grep "Content-Length"
# < Content-Length: 5000
# Transfer: 5000 bytes

# Z kompresją
curl -v --compressed http://example.com/api/users 2>&1 | grep "Content-Length"
# < Content-Length: 1200
# Transfer: 1200 bytes (76% oszczędności!)

# Output w OBIE strony wygląda tak samo (curl rozpakował):
# [{"id": 1, "name": "John"}, ...]
```

#### curl verbose mode - zobacz co się dzieje

```bash
curl -v --compressed http://example.com/api/users

# Request Headers (curl wysyła):
> GET /api/users HTTP/1.1
> Host: example.com
> Accept-Encoding: gzip, deflate  ← curl dodał automatycznie (--compressed)

# Response Headers (serwer odpowiada):
< HTTP/1.1 200 OK
< Content-Type: application/json
< Content-Encoding: gzip  ← Serwer skompresował!
< Content-Length: 1200    ← Rozmiar skompresowany

# Output (curl automatycznie rozpakował):
[{"id": 1, "name": "John"}, ...]
```

#### Kiedy curl NIE rozpakuje automatycznie?

```bash
# Tylko gdy zapiszesz do pliku PRZED rozpakowaniem:
curl -H "Accept-Encoding: gzip" --output file.gz http://example.com/api/users
# file.gz = skompresowane dane (binary)

# curl NIE rozpakował, bo użyłeś --output przed rozpakowaniem
# Musisz ręcznie: gunzip file.gz
```

#### Best practices z curl i gzip

```bash
# ✅ DOBRZE - używaj --compressed dla normalnego użycia
curl --compressed http://example.com/api/users

# ✅ DOBRZE - verbose mode dla debugowania
curl -v --compressed http://example.com/api/users

# ✅ DOBRZE - zapisz ROZPAKOWANE dane do pliku
curl --compressed http://example.com/api/users > output.json
# output.json = zdekompresowane dane ✅

# ❌ ŹLE - nie mieszaj --output z kompresją (chyba że chcesz raw gzip)
curl --compressed --output file.json http://example.com/api/users
# file.json może być gzip lub nie (zależy od implementacji curl)

# ✅ LEPIEJ - użyj przekierowania zamiast --output
curl --compressed http://example.com/api/users > file.json
```

#### Python requests vs curl

**Python requests:**
```python
import requests

# requests AUTOMATYCZNIE obsługuje gzip!
response = requests.get('http://example.com/api/users')
# requests wysyła Accept-Encoding: gzip, deflate
# requests automatycznie rozpakowuje

print(response.text)  # Zdekompresowane dane
print(response.headers['Content-Encoding'])  # 'gzip' (ale już rozpakowane)
```

**curl:**
```bash
# Equivalent curl command:
curl --compressed http://example.com/api/users

# Oba robią to samo:
# 1. Wysyłają Accept-Encoding
# 2. Rozpakowują automatycznie
# 3. Zwracają zdekompresowane dane
```

#### Testing gzip compression na serwerze

```bash
# Test czy serwer kompresuje
curl -v --compressed http://example.com/api/users 2>&1 | grep -i "content-encoding"

# Jeśli widzisz:
# < Content-Encoding: gzip
# → Serwer KOMPRESUJE ✅

# Jeśli nie widzisz tego headera:
# → Serwer NIE kompresuje ❌ (sprawdź nginx config: gzip on;)
```

#### Podsumowanie - curl i gzip:

| Komenda | Accept-Encoding wysyłany? | Automatyczne rozpakowanie? | Output |
|---------|---------------------------|----------------------------|--------|
| `curl URL` | ❌ NIE | N/A (brak kompresji) | Plain text |
| `curl --compressed URL` | ✅ TAK (auto) | ✅ TAK | Zdekompresowane |
| `curl -H "Accept-Encoding: gzip" URL` | ✅ TAK (manual) | ✅ TAK | Zdekompresowane |
| `curl -H "Accept-Encoding: gzip" --output file.gz URL` | ✅ TAK | ❌ NIE (zapisano raw) | Binary gzip |

**Najłatwiejszy sposób:** `curl --compressed URL` ✅

---

### Browser DevTools:

**Chrome DevTools → Network tab:**

```
Request Headers:
  Accept-Encoding: gzip, deflate, br

Response Headers:
  Content-Encoding: gzip
  Content-Length: 1200 (compressed size)

Size:
  1.2 KB (transferred)  ← gzip size (over network)
  5.0 KB (resource)     ← original size (after decompression)
```

Browser automatycznie:
1. Wysyła `Accept-Encoding: gzip`
2. Dostaje response z `Content-Encoding: gzip`
3. Rozpakowuje gzip
4. Parsuje JSON
5. Renderuje stronę

**Użytkownik nie widzi kompresji - wszystko automatyczne!**

### Vary header - ważny!

```nginx
gzip_vary on;  # Dodaje: Vary: Accept-Encoding
```

**Po co `Vary: Accept-Encoding`?**

```http
# Response z gzip:
HTTP/1.1 200 OK
Content-Encoding: gzip
Vary: Accept-Encoding  ← WAŻNY!
```

**`Vary: Accept-Encoding`** mówi cache'om (CDN, browser cache):

> "Ten response zależy od `Accept-Encoding` headera.
> Cache osobno dla gzip i non-gzip requests!"

**Bez `Vary`:**
```
Request 1 (z Accept-Encoding: gzip):
  → Response: gzip (cached)

Request 2 (BEZ Accept-Encoding):
  → Response: gzip z cache ← ŹLE! (klient nie umie rozpakować)
```

**Z `Vary`:**
```
Request 1 (z Accept-Encoding: gzip):
  → Response: gzip (cached jako "gzip version")

Request 2 (BEZ Accept-Encoding):
  → Response: uncompressed (cached jako "plain version")
```

### Kompresja tylko dla text-based:

```nginx
gzip_types
    text/plain
    text/css
    application/json
    application/javascript
    text/xml;
```

**NIE kompresuj:**
- Images (już skompresowane: JPEG, PNG, WebP)
- Videos (już skompresowane: MP4, WebM)
- Compressed archives (ZIP, tar.gz)

**Przykład:**
```bash
# JSON (text-based) - duża kompresja
Original: 5000 bytes
gzip: 1200 bytes (76% savings!)

# JPEG (binary, już skompresowany) - prawie brak kompresji
Original: 50000 bytes
gzip: 49800 bytes (0.4% savings - nie warto!)
```

### Compression algorithms:

| Algorithm | Header | Compression | Speed | Browser support |
|-----------|--------|-------------|-------|-----------------|
| **gzip** | `Content-Encoding: gzip` | Good | Fast | ✅ 100% |
| **deflate** | `Content-Encoding: deflate` | Good | Fast | ✅ 100% |
| **br** (Brotli) | `Content-Encoding: br` | Better | Slower | ✅ Modern browsers |

**Brotli (br)** - lepszy niż gzip (nowszy):
```nginx
# nginx z Brotli module
brotli on;
brotli_types text/plain text/css application/json;

# Request:
Accept-Encoding: gzip, deflate, br

# Response (nginx wybiera najlepszy):
Content-Encoding: br  # Brotli (lepszy niż gzip)
```

### 🔍 Czy gzip compression ma sens dla REST API?

**Pytanie:** Czy kompresja gzip ma sens dla JSON API, czy to tylko dla HTML/CSS/JS?

**Odpowiedź: TAK! gzip ma OGROMNY sens dla JSON API!** 🚀

#### Dlaczego JSON kompresuje się świetnie?

**JSON to tekst z dużą ilością powtarzających się wzorców:**

```json
// Przykładowy response z API:
[
  {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30},
  {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 25},
  {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "age": 35},
  // ... 100 więcej obiektów
]
```

**Powtarzające się wzorce:**
- Klucze: `"id"`, `"name"`, `"email"`, `"age"` (powtarzają się 100 razy!)
- Struktura: `{...}`, `[...]`, przecinki, nawiasy
- Podobne wartości: `"@example.com"`, liczby

**gzip doskonale kompresuje powtórzenia → 70-90% oszczędności!**

#### Benchmarki kompresji dla różnych wielkości JSON:

| Wielkość response | Oryginalny rozmiar | Po gzip | Oszczędność | Czy warto? |
|-------------------|-------------------|---------|-------------|------------|
| **Bardzo mały** | 500 bytes | 400 bytes | 20% | ❌ NIE (overhead > korzyść) |
| **Mały** | 2 KB | 800 bytes | 60% | ✅ TAK (jeśli `gzip_min_length 1000`) |
| **Średni** | 10 KB | 2.5 KB | 75% | ✅ TAK! |
| **Duży** | 50 KB | 8 KB | 84% | ✅ TAK! |
| **Bardzo duży** | 500 KB | 50 KB | 90% | ✅ TAK! |
| **Image (JPEG)** | 100 KB | 99.5 KB | 0.5% | ❌ NIE (już skompresowany) |

#### Przykład real-world (lista userów):

**Bez gzip:**
```bash
curl http://api.example.com/users?limit=100

# Response:
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 50000  # 50 KB

[{"id": 1, "name": "John", ...}, ...]
# Transfer: 50 KB przez sieć
# Czas: ~500ms (przy 1 Mbps)
```

**Z gzip:**
```bash
curl --compressed http://api.example.com/users?limit=100

# Response:
HTTP/1.1 200 OK
Content-Type: application/json
Content-Encoding: gzip
Content-Length: 8000  # 8 KB (skompresowane!)

[binary gzip data]
# Transfer: 8 KB przez sieć (zamiast 50 KB!)
# Czas: ~80ms (przy 1 Mbps)

# curl automatycznie rozpakował:
[{"id": 1, "name": "John", ...}, ...]
```

**Oszczędność:**
- **Bandwidth:** 42 KB (84% mniej!)
- **Transfer time:** 420ms szybciej!
- **Koszt CPU:** ~10ms (kompresja + dekompresja)
- **Net benefit:** 410ms szybciej! 🚀

#### Kiedy gzip MA sens dla API?

✅ **Użyj gzip gdy:**

1. **Duże JSON responses (>10 KB):**
   - Listy obiektów (users, products, orders)
   - Nested objects (duże drzewa kategorii, komentarze)
   - Oszczędność: 80-90%

2. **Średnie JSON responses (1-10 KB):**
   - Single resource z relacjami (user + posts + comments)
   - Search results
   - Oszczędność: 60-80%

3. **Text-based formats:**
   - CSV exports
   - XML (SOAP APIs)
   - GraphQL responses
   - Oszczędność: 70-85%

4. **Mobile apps:**
   - Mobile network jest wolniejszy → transfer time > CPU time
   - Oszczędność bandwidth = oszczędność baterii!

5. **Wolne sieci:**
   - Publiczne Wi-Fi
   - 3G/4G
   - Overseas connections
   - Transfer time >> CPU time → gzip ZAWSZE warto!

#### Kiedy gzip NIE ma sensu dla API?

❌ **NIE używaj gzip gdy:**

1. **Bardzo małe responses (<1 KB):**
   - Single user: `{"id": 1, "name": "John"}` (100 bytes)
   - Status check: `{"status": "ok"}` (20 bytes)
   - Overhead gzip > oszczędność

2. **Już skompresowane dane:**
   - Images (JPEG, PNG, WebP) - API zwraca base64 lub URL
   - Binary files (PDF, ZIP, videos)
   - Kompresja ~0%, overhead > korzyść

3. **Streaming responses:**
   - Server-Sent Events (SSE)
   - Chunked transfer
   - gzip bufferuje dane (nie działa dla streaming)

4. **Real-time messaging:**
   - WebSocket messages (każda wiadomość mała, overhead duży)
   - Chat messages (20-200 bytes każda)
   - Latency ważniejsza niż bandwidth

#### nginx konfiguracja dla JSON API:

```nginx
http {
    # Włącz gzip
    gzip on;

    # Minimalna wielkość response (nie kompresuj <1KB)
    gzip_min_length 1000;  # 1 KB = sweet spot

    # Typy dla JSON API
    gzip_types
        application/json       # JSON API responses ← GŁÓWNE!
        application/javascript # JS files
        text/plain            # Text responses
        text/csv;             # CSV exports

    # Poziom kompresji (1-9)
    gzip_comp_level 6;  # Sweet spot: dobra kompresja + szybko
    # 1 = najszybsze, słaba kompresja
    # 6 = balans (recommended)
    # 9 = najlepsza kompresja, wolne (nie warto, marginalny zysk)

    # Proxy support (dla reverse proxy)
    gzip_proxied any;

    # Vary header (ważne dla cache)
    gzip_vary on;
}
```

**Dlaczego `gzip_comp_level 6`?**

| Level | Kompresja | Czas CPU | Oszczędność vs level 1 | Koszt CPU vs level 1 |
|-------|-----------|----------|------------------------|----------------------|
| 1 | 65% | 5ms | - | - |
| 6 | 75% | 10ms | +10% | 2x |
| 9 | 77% | 30ms | +12% | 6x |

**Level 6 = sweet spot:**
- 75% kompresji (tylko 2% gorszej niż level 9)
- 3x szybsze niż level 9
- **Best cost/benefit ratio!**

#### Real-world impact dla JSON API:

**Scenariusz:** REST API zwracające listy obiektów

```python
# FastAPI endpoint
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/users")
async def get_users(limit: int = 100):
    # Response: lista 100 userów
    return [
        {"id": i, "name": f"User {i}", "email": f"user{i}@example.com"}
        for i in range(limit)
    ]
```

**Bez gzip:**
```bash
# Response size: 15 KB (100 users)
# Transfer time (1 Mbps): ~120ms
# CPU time: 0ms
# Total: 120ms
```

**Z gzip:**
```bash
# Response size: 3 KB (80% kompresja!)
# Transfer time (1 Mbps): ~24ms
# CPU time (kompresja + dekompresja): ~8ms
# Total: 32ms

# Zysk: 88ms (73% szybciej!)
```

**Bandwidth savings (1 million requests/day):**
```
Bez gzip: 15 KB × 1M = 15 GB/day = 450 GB/month
Z gzip:   3 KB × 1M  = 3 GB/day  = 90 GB/month

Oszczędność: 360 GB/month (80%!)
Koszt (AWS, $0.09/GB): $32.40/month oszczędności!
```

#### CPU cost vs Network savings:

**Network transfer time:** (przy typowym 1 Mbps connection)
- 50 KB response: ~400ms
- 8 KB response (gzip): ~64ms
- **Oszczędność: 336ms**

**CPU cost:**
- Kompresja (nginx, gzip level 6): ~8ms
- Dekompresja (client): ~2ms
- **Koszt: 10ms**

**Net benefit: 326ms szybciej!**

**Network jest o wiele wolniejsze niż CPU:**
- Network bandwidth: 1 Mbps = 125 KB/s
- CPU: może skompresować 50 MB/s (400x szybciej!)
- **Nawet przy 100 Mbps network, gzip nadal warto (mniej overhead latency)!**

#### Mobile API considerations:

**Mobile networks są wolniejsze:**
- 3G: ~1 Mbps (typowo)
- 4G: ~10 Mbps (typowo, ale unstable)
- 5G: ~100 Mbps (ale coverage niski)

**Mobile CPU:**
- Nowoczesne smartfony: dekompresja gzip ~5ms (marginalny koszt)
- Oszczędność battery przez mniejszy transfer danych!

**Dla mobile API: gzip to MUST-HAVE!**

#### GraphQL API - gzip jeszcze ważniejsze!

GraphQL responses często bardzo duże (nested queries):

```graphql
query {
  users {
    id
    name
    posts {
      id
      title
      comments {
        id
        text
        author { id, name }
      }
    }
  }
}
```

**Response:** 500 KB (nested data)
**Po gzip:** 50 KB (90% kompresja!)

**GraphQL = duże responses = gzip MUST-HAVE!**

#### Testing gzip dla swojego API:

```bash
# Test bez gzip
time curl http://localhost:8000/api/users?limit=1000

# Test z gzip
time curl --compressed http://localhost:8000/api/users?limit=1000

# Compare bandwidth
curl -v http://localhost:8000/api/users 2>&1 | grep "Content-Length"
curl -v --compressed http://localhost:8000/api/users 2>&1 | grep "Content-Length"

# Porównaj transfer time (real time)
# Bez gzip: real 0m0.523s
# Z gzip:   real 0m0.095s
# Zysk: 428ms (81% szybciej!)
```

### Podsumowanie:

**Jak klient wie że musi rozpakować?**

1. Klient wysyła: `Accept-Encoding: gzip` ("umiem gzip")
2. Serwer kompresuje i dodaje: `Content-Encoding: gzip` ("to jest gzip")
3. Klient widzi header i automatycznie rozpakuje

**Skąd wie JAK rozpakować?**

- `Content-Encoding: gzip` → użyj gzip decompression
- `Content-Encoding: br` → użyj Brotli decompression
- `Content-Encoding: deflate` → użyj deflate decompression

**Wszystko automatyczne:**
- Browser/curl automatycznie wysyła `Accept-Encoding`
- nginx automatycznie kompresuje (jeśli `gzip on;`)
- Browser/curl automatycznie rozpakowuje (jeśli widzi `Content-Encoding`)

**Korzyści:**
- Mniej danych przez sieć (5000 → 1200 bytes)
- Szybsze ładowanie (mniej transfer time)
- Oszczędność bandwidth

**Koszt:**
- CPU serwera (kompresja)
- CPU klienta (dekompresja)
- Ale warto! (network jest wolniejsze niż CPU)

**Dla JSON API:**
- ✅ **ZAWSZE włączaj gzip** dla responses >1 KB
- ✅ Oszczędność: 70-90% bandwidth
- ✅ Transfer time: 3-5x szybciej
- ✅ CPU cost: marginalny (~10ms)
- ✅ Mobile: jeszcze ważniejsze (wolniejsza sieć + oszczędność baterii)
- ✅ GraphQL: must-have (duże nested responses)
- ❌ NIE używaj dla responses <1 KB (overhead > korzyść)
- ❌ NIE używaj dla binary data (images, videos, PDFs)

---

## 12. Konteneryzacja - architektura Docker

**Pytanie:** Brakuje jeszcze opisu konteneryzacji API, czy każdy element ma mieć oddzielny kontener: http serwer, wsgi serwer, application, ...?

**Odpowiedź:**

Świetne pytanie! To będzie osobny temat do osobnego pliku.

### Szybka odpowiedź:

**NIE**, w jednym kontenerze możesz mieć:
- nginx + Gunicorn + FastAPI app
- Albo osobne kontenery dla każdego (lepsze dla skalowalności)

**Najlepsza praktyka:** Osobne kontenery dla każdej usługi (microservices approach).

### Architektura 1: Monolithic Container (wszystko w jednym)

```
┌──────────────────────────────────┐
│      Docker Container            │
│  ┌────────────────────────────┐  │
│  │  nginx (reverse proxy)     │  │
│  └────────────────────────────┘  │
│              ↓                    │
│  ┌────────────────────────────┐  │
│  │  Gunicorn (WSGI server)    │  │
│  └────────────────────────────┘  │
│              ↓                    │
│  ┌────────────────────────────┐  │
│  │  FastAPI app               │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Install nginx
RUN apt-get update && apt-get install -y nginx

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . /app
WORKDIR /app

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Supervisor to run both nginx + Gunicorn
RUN apt-get install -y supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose port
EXPOSE 80

CMD ["/usr/bin/supervisord"]
```

**Zalety:**
- ✅ Prosty deployment (1 kontener)
- ✅ Mniej overhead

**Wady:**
- ❌ Trudne skalowanie (całość razem)
- ❌ Restart jednego = restart wszystkiego
- ❌ Trudniejszy maintenance

**Kiedy:** Małe projekty, proof-of-concept

---

### Architektura 2: Multi-container (RECOMMENDED)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  nginx          │───→│  web (Gunicorn) │───→│  PostgreSQL     │
│  Container      │    │  Container      │    │  Container      │
│  port 80/443    │    │  port 8000      │    │  port 5432      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ↓
                       ┌─────────────────┐
                       │  Redis          │
                       │  Container      │
                       │  port 6379      │
                       └─────────────────┘
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  # 1. PostgreSQL Database
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: fastapi_user
      POSTGRES_PASSWORD: fastapi_password
      POSTGRES_DB: fastapi_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fastapi_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # 2. Redis Cache
  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # 3. FastAPI App (Gunicorn + Uvicorn workers)
  web:
    build: .
    command: >
      gunicorn main:app
      --workers 4
      --worker-class uvicorn.workers.UvicornWorker
      --bind 0.0.0.0:8000
      --timeout 30
      --graceful-timeout 30
      --log-level info
    volumes:
      - ./app:/app  # Dev: mount code
      - static_volume:/app/static  # Static files
      - media_volume:/app/media  # User uploads
    expose:
      - 8000  # Internal only (not published to host)
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://fastapi_user:fastapi_password@db:5432/fastapi_db
      - REDIS_URL=redis://redis:6379/0

  # 4. nginx (Reverse Proxy)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"      # HTTP
      - "443:443"    # HTTPS
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro  # SSL certificates
      - static_volume:/var/www/static:ro  # Static files (shared with web)
      - media_volume:/var/www/media:ro  # Media files (shared with web)
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

**Zalety:**
- ✅ Osobne skalowanie każdego serwisu
- ✅ Izolacja (restart nginx nie wpływa na app)
- ✅ Łatwe update'y (tylko jeden kontener)
- ✅ Best practice (microservices)

**Wady:**
- ⚠️ Więcej konfiguracji
- ⚠️ Więcej kontenerów (ale docker-compose to upraszcza)

**Kiedy:** Produkcja, aplikacje do skalowania

---

### Dockerfile dla FastAPI (web service):

```dockerfile
# Dockerfile (dla web service)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create static/media directories
RUN mkdir -p /app/static /app/media

# Expose port (documentation only, not actually published)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run Gunicorn with Uvicorn workers
CMD ["gunicorn", "main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "30", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

---

### nginx config (dla reverse proxy):

```nginx
# nginx/nginx.conf
upstream backend {
    # Load balance between multiple web containers (if scaled)
    server web:8000;  # Docker service name
}

server {
    listen 80;
    server_name example.com;

    # Max upload size
    client_max_body_size 10M;

    # Static files (nginx serwuje bezpośrednio)
    location /static/ {
        alias /var/www/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/media/;
        expires 7d;
    }

    # API requests (proxy to Gunicorn)
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint
    location /nginx-health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

---

### Deployment:

```bash
# 1. Build i uruchom wszystko
docker-compose up -d --build

# Co się dzieje:
# - Buduje obraz dla 'web' service
# - Pobiera obrazy: postgres, redis, nginx
# - Tworzy network (wszystkie kontenery mogą się komunikować)
# - Uruchamia kontenery w kolejności (depends_on)

# 2. Sprawdź status
docker-compose ps
# NAME                COMMAND                  SERVICE   STATUS    PORTS
# myapp-db-1          "docker-entrypoint.s…"   db        Up        5432/tcp
# myapp-redis-1       "docker-entrypoint.s…"   redis     Up        6379/tcp
# myapp-web-1         "gunicorn main:app -…"   web       Up        8000/tcp
# myapp-nginx-1       "nginx -g 'daemon of…"   nginx     Up        0.0.0.0:80->80/tcp

# 3. Logi
docker-compose logs -f web  # FastAPI logs
docker-compose logs -f nginx  # nginx logs

# 4. Health check
curl http://localhost/health

# 5. Skalowanie web service
docker-compose up -d --scale web=4
# Teraz 4 kontenery 'web', nginx load balances między nimi

# 6. Restart pojedynczego serwisu (bez downtime całości)
docker-compose restart web

# 7. Update kodu (rebuild + restart)
docker-compose up -d --build web
```

---

### Kubernetes Alternative (advanced):

**Dla dużych deploymentów:**

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 4  # 4 pods (każdy = web container)
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: web
        image: myregistry/fastapi-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer  # Kubernetes load balancer (zamiast nginx)
```

**Kubernetes daje:**
- Auto-scaling (więcej pods gdy traffic rośnie)
- Auto-healing (restart crashed pods)
- Load balancing (built-in)
- Rolling updates (zero-downtime)

---

### Podsumowanie - Kontenery:

#### Opcja 1: Single Container (wszystko w jednym)
```
1 kontener:
  - nginx
  - Gunicorn
  - FastAPI

Kiedy: Małe projekty, dev/test
```

#### Opcja 2: Multi-Container (RECOMMENDED)
```
nginx kontener
web kontener (Gunicorn + FastAPI)
db kontener (PostgreSQL)
redis kontener

Kiedy: Produkcja, skalowalne aplikacje
```

#### Opcja 3: Kubernetes (enterprise)
```
Kubernetes Pods (web replicas)
Kubernetes Services (load balancing)
Managed DB (RDS, Cloud SQL)
Managed Redis (ElastiCache)

Kiedy: Duże aplikacje, auto-scaling, cloud-native
```

**Best practice:**
- **Development:** Docker Compose (multi-container)
- **Production (small/medium):** Docker Compose + Docker Swarm
- **Production (large):** Kubernetes

**To będzie osobny materiał:** `06_docker_deployment.ipynb`

---

## 13. Inne ważne tematy deployment

**Pytanie:** Jakieś tematy o których zapomniałem a są istotne w temacie API deployment CI/CD production?

**Odpowiedź:**

Tak! Oto kluczowe tematy które warto dodać:

### 1. **CI/CD (Continuous Integration/Continuous Deployment)**

```yaml
# .github/workflows/deploy.yml (GitHub Actions)
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install pytest
          pytest tests/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
        run: docker build -t myapp:latest .

      - name: Push to registry
        run: docker push myregistry/myapp:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        run: |
          ssh user@server "docker pull myregistry/myapp:latest"
          ssh user@server "docker-compose up -d"
```

**Tematy:**
- GitHub Actions / GitLab CI / Jenkins
- Automated testing (pytest)
- Docker registry (Docker Hub, AWS ECR, GitLab Registry)
- Deployment strategies (blue-green, canary, rolling)

---

### 2. **Environment Variables & Secrets Management**

```python
# settings.py (Pydantic Settings)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    api_key: str

    class Config:
        env_file = ".env"  # Development
        # Production: read from environment variables

settings = Settings()
```

**Tematy:**
- `.env` files (development)
- Environment variables (production)
- Secrets management (AWS Secrets Manager, HashiCorp Vault, Kubernetes Secrets)
- Never commit secrets to git!

---

### 3. **Database Migrations**

```python
# Alembic (SQLAlchemy migrations)
alembic init migrations
alembic revision --autogenerate -m "create users table"
alembic upgrade head  # Apply migrations in production
```

**Tematy:**
- Alembic (for SQLAlchemy)
- Django migrations
- Zero-downtime migrations
- Rollback strategy

---

### 4. **Monitoring & Observability**

```python
# Sentry (error tracking)
import sentry_sdk
sentry_sdk.init(dsn="https://...")

# Prometheus (metrics)
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

# Grafana dashboards
```

**Tematy:**
- Error tracking (Sentry, Rollbar)
- Metrics (Prometheus + Grafana)
- Logging (ELK stack, Loki)
- APM (Application Performance Monitoring - DataDog, New Relic)
- Distributed tracing (Jaeger, Zipkin)

---

### 5. **Backup & Disaster Recovery**

```bash
# PostgreSQL backup
pg_dump -U user -h localhost dbname > backup.sql

# Automated backups (cron)
0 2 * * * /usr/bin/pg_dump -U user dbname | gzip > /backups/db-$(date +\%Y\%m\%d).sql.gz

# Restore
gunzip backup.sql.gz
psql -U user dbname < backup.sql
```

**Tematy:**
- Database backups (automated)
- Point-in-time recovery
- Disaster recovery plan
- Backup testing (czy backup działa?)

---

### 6. **Security Best Practices**

```python
# CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],  # NOT "*" in production!
    allow_credentials=True,
)

# Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
@app.get("/api/users")
@limiter.limit("5/minute")
def get_users():
    ...

# SQL Injection protection (use ORM!)
# XSS protection (escape user input)
# CSRF tokens (dla form submissions)
```

**Tematy:**
- HTTPS/SSL (Let's Encrypt)
- CORS configuration
- Rate limiting
- SQL injection prevention
- XSS/CSRF protection
- Security headers (nginx)
- Dependency scanning (Snyk, Dependabot)

---

### 7. **Performance Optimization**

```python
# Caching (Redis)
import redis
cache = redis.Redis(host='localhost', port=6379)

@app.get("/api/users")
async def get_users():
    cached = cache.get("users")
    if cached:
        return json.loads(cached)

    users = await db.fetch_all("SELECT * FROM users")
    cache.setex("users", 300, json.dumps(users))  # Cache 5 min
    return users

# Database connection pooling
# CDN for static files (Cloudflare, AWS CloudFront)
# Database indexing
# Query optimization
```

**Tematy:**
- Caching strategies (Redis, Memcached)
- Database optimization (indexes, query optimization)
- CDN for static files
- Load testing (Locust, k6)
- Profiling (py-spy, cProfile)

---

### 8. **Scaling Strategies**

**Horizontal Scaling:**
```yaml
# docker-compose.yml
docker-compose up -d --scale web=10  # 10 web containers
```

**Vertical Scaling:**
```yaml
# Bigger server (more CPU/RAM)
web:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
```

**Tematy:**
- Horizontal vs Vertical scaling
- Load balancing (nginx, HAProxy, cloud load balancers)
- Auto-scaling (Kubernetes HPA, AWS Auto Scaling)
- Database scaling (read replicas, sharding)

---

### 9. **Health Checks & Readiness Probes**

```python
# FastAPI health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/readiness")
async def readiness_check():
    # Check DB connection
    try:
        await db.execute("SELECT 1")
        return {"status": "ready"}
    except:
        raise HTTPException(status_code=503, detail="not ready")
```

**Kubernetes:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /readiness
    port: 8000
```

---

### 10. **Logging Best Practices**

```python
# Structured logging (JSON)
import structlog

logger = structlog.get_logger()

@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    logger.info("user_fetch", user_id=user_id, action="fetch")
    # Output: {"event": "user_fetch", "user_id": 123, "action": "fetch", "timestamp": "..."}
```

**Tematy:**
- Structured logging (JSON format)
- Log aggregation (ELK, Loki, Papertrail)
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Request ID tracking (dla distributed systems)

---

### 11. **Blue-Green Deployment**

```
Production Traffic → Green (current version)

Deploy:
1. Deploy Blue (new version) - no traffic yet
2. Test Blue
3. Switch traffic: Green → Blue
4. Keep Green running (rollback option)
5. After verification, shut down Green
```

**Zero downtime!**

---

### 12. **Infrastructure as Code (IaC)**

```hcl
# Terraform example
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.medium"

  tags = {
    Name = "FastAPI-Server"
  }
}

resource "aws_rds_instance" "db" {
  engine         = "postgres"
  instance_class = "db.t3.micro"
}
```

**Tematy:**
- Terraform
- AWS CloudFormation
- Ansible
- Version control for infrastructure

---

### 13. **API Versioning**

```python
# URL versioning
@app.get("/api/v1/users")
def get_users_v1():
    ...

@app.get("/api/v2/users")
def get_users_v2():
    # Breaking changes OK - different endpoint
    ...

# Header versioning
@app.get("/api/users")
def get_users(request: Request):
    version = request.headers.get("API-Version", "1")
    if version == "2":
        return users_v2()
    return users_v1()
```

---

### 14. **WSGI/ASGI Middleware**

```python
# Custom middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Authentication middleware
# CORS middleware
# Logging middleware
# Rate limiting middleware
```

---

### Podsumowanie - Lista tematów do dodania:

1. ✅ **CI/CD pipelines** (GitHub Actions, GitLab CI)
2. ✅ **Secrets management** (environment variables, vaults)
3. ✅ **Database migrations** (Alembic)
4. ✅ **Monitoring** (Sentry, Prometheus, Grafana)
5. ✅ **Backups & disaster recovery**
6. ✅ **Security** (CORS, rate limiting, SSL)
7. ✅ **Performance** (caching, CDN, optimization)
8. ✅ **Scaling** (horizontal/vertical, load balancing)
9. ✅ **Health checks** (liveness/readiness probes)
10. ✅ **Logging** (structured, aggregation)
11. ✅ **Deployment strategies** (blue-green, canary, rolling)
12. ✅ **Infrastructure as Code** (Terraform, Ansible)
13. ✅ **API versioning**
14. ✅ **Middleware patterns**

**Te tematy warto dodać do materiałów jako:**
- `06_docker_deployment.ipynb` (Docker + docker-compose)
- `07_cicd_monitoring.ipynb` (CI/CD, monitoring, logging)
- `08_production_best_practices.ipynb` (security, performance, scaling)

---

## 14. Starlette - co to i jak się ma do FastAPI/ASGI/Uvicorn?

**Pytanie:** W materiałach o deployment jest WSGI, ASGI, Uvicorn, Gunicorn, nginx, FastAPI - ale nigdzie nie ma Starlette. Co to jest Starlette i jak się wpisuje w ten ekosystem?

**Odpowiedź:**

ŚWIETNE pytanie! Starlette to **kluczowy element** dla zrozumienia FastAPI, ale często pomijany w materiałach.

### Szybka odpowiedź:

**Starlette = low-level ASGI framework, na którym zbudowany jest FastAPI**

```
FastAPI jest do Starlette
jak
Django jest do Python
```

**FastAPI NIE JEST samodzielnym frameworkiem** - to warstwa abstrakcji NA Starlette!

---

### Hierarchia - Pełny stack:

```
┌─────────────────────────────────────┐
│  nginx (HTTP Server + Reverse Proxy)│  ← Warstwa 1: HTTP Server
└──────────────┬──────────────────────┘
               │ proxy_pass
               ↓
┌─────────────────────────────────────┐
│  Uvicorn (ASGI Server)              │  ← Warstwa 2: Implementacja standardu ASGI
│  - HTTP parsing                     │     (mapuje HTTP → Python callable)
│  - Event loop (asyncio)             │
│  - Wywołuje aplikację ASGI          │
└──────────────┬──────────────────────┘
               │ uruchamia aplikację ASGI
               ↓
┌─────────────────────────────────────┐
│  FastAPI + Starlette                │  ← Warstwa 3: Twoja aplikacja Python
│                                     │
│  FastAPI (zbudowane NA Starlette):  │
│  - Walidacja (Pydantic)             │
│  - Dependency Injection             │
│  - OpenAPI docs                     │
│  - Automatic serialization          │
│                                     │
│  Starlette (core toolkit):          │
│  - Routing                          │
│  - Middleware                       │
│  - Request/Response handling        │
│  - WebSockets                       │
│  - Background tasks                 │
└─────────────────────────────────────┘

ASGI = Standard/Interface (specyfikacja mówiąca JAK Uvicorn ma komunikować się z aplikacją Python)
```

**FastAPI = Starlette + Pydantic + dodatkowe features**

**UWAGA:** ASGI to NIE warstwa w architekturze - to **standard/protokół** który Uvicorn **implementuje**!

---

### Co to jest Starlette?

**Starlette = lightweight ASGI framework (jak Werkzeug dla Flask)**

**Autor:** Tom Christie (ten sam co Django REST Framework!)

**Rok:** 2018

**Cechy:**
- Minimalistyczny ASGI framework
- Bardzo szybki (performance-focused)
- Routing, middleware, requests/responses
- WebSockets support
- Background tasks
- Testing utilities

**Kod Starlette:**

```python
# Pure Starlette (bez FastAPI)
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

async def homepage(request):
    return JSONResponse({'message': 'Hello World'})

async def user(request):
    user_id = request.path_params['user_id']
    return JSONResponse({'user_id': user_id})

app = Starlette(routes=[
    Route('/', homepage),
    Route('/users/{user_id}', user),
])

# Uruchom: uvicorn main:app
```

**To jest PURE Starlette - bez FastAPI!**

---

### FastAPI vs Starlette - Co dodaje FastAPI?

**FastAPI = Starlette + DUŻO więcej**

| Feature | Starlette | FastAPI |
|---------|-----------|---------|
| **Routing** | ✅ TAK | ✅ TAK (używa Starlette) |
| **Request/Response** | ✅ TAK | ✅ TAK (używa Starlette) |
| **Middleware** | ✅ TAK | ✅ TAK (używa Starlette) |
| **WebSockets** | ✅ TAK | ✅ TAK (używa Starlette) |
| **Walidacja (Pydantic)** | ❌ NIE | ✅ TAK |
| **Type hints → validation** | ❌ NIE | ✅ TAK |
| **Dependency Injection** | ❌ NIE | ✅ TAK |
| **OpenAPI docs** | ❌ NIE | ✅ TAK |
| **Auto serialization** | ❌ NIE | ✅ TAK |
| **OAuth2/JWT helpers** | ❌ NIE | ✅ TAK |

**FastAPI dodaje:**
1. **Pydantic** - walidacja + serialization
2. **Dependency Injection**
3. **OpenAPI/Swagger** - automatyczna dokumentacja
4. **Type hints** → automatic validation
5. **Security utilities** (OAuth2, JWT)

---

### Przykład: Ten sam endpoint w Starlette vs FastAPI

#### Starlette (pure):

```python
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import json

async def create_user(request):
    # ❌ Ręczna walidacja!
    body = await request.body()
    data = json.loads(body)

    # ❌ Ręczne sprawdzanie!
    if 'name' not in data or 'email' not in data:
        return JSONResponse({'error': 'Missing fields'}, status_code=400)

    # ❌ Ręczne sprawdzanie typów!
    if not isinstance(data['name'], str):
        return JSONResponse({'error': 'Name must be string'}, status_code=400)

    # ❌ Ręczna logika biznesowa
    user = {'id': 123, 'name': data['name'], 'email': data['email']}

    # ❌ Ręczna serializacja do JSON!
    return JSONResponse(user, status_code=201)

app = Starlette(routes=[
    Route('/users', create_user, methods=['POST']),
])
```

#### FastAPI:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: str

@app.post("/users", status_code=201)
async def create_user(user: UserCreate):
    # ✅ Walidacja automatyczna (Pydantic)!
    # ✅ Type checking automatyczny!
    # ✅ Serializacja automatyczna!
    # ✅ OpenAPI docs automatyczne!

    return {'id': 123, **user.dict()}
```

**FastAPI robi ZA CIEBIE:**
- Parsing JSON
- Walidacja (name is str, email is str)
- Type checking
- Error responses (422 Unprocessable Entity)
- Serializacja response do JSON
- OpenAPI documentation

**Starlette wymaga RĘCZNEGO kodu!**

---

### Kiedy widać Starlette w FastAPI?

**FastAPI używa Starlette "pod maską":**

#### 1. **Request/Response obiekty:**

```python
from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse  # ← Starlette!

app = FastAPI()

@app.get("/")
async def root(request: Request):  # ← Request to Starlette Request!
    return {"client": request.client.host}  # Starlette API

@app.get("/html", response_class=HTMLResponse)  # ← Starlette Response!
async def html():
    return "<html><body>Hello</body></html>"
```

#### 2. **Middleware:**

```python
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware  # ← Starlette!

app = FastAPI()

app.add_middleware(  # ← FastAPI używa Starlette middleware!
    CORSMiddleware,
    allow_origins=["*"],
)
```

#### 3. **Background Tasks:**

```python
from fastapi import FastAPI, BackgroundTasks  # ← Wraps Starlette!

app = FastAPI()

def send_email(email: str):
    print(f"Sending email to {email}")

@app.post("/send-notification")
async def send_notification(background_tasks: BackgroundTasks):
    # BackgroundTasks = Starlette feature!
    background_tasks.add_task(send_email, "user@example.com")
    return {"message": "Notification sent"}
```

#### 4. **WebSockets:**

```python
from fastapi import FastAPI, WebSocket  # ← Wraps Starlette WebSocket!

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # ← Starlette WebSocket API
    await websocket.send_text("Hello")
```

**FastAPI eksponuje Starlette API w wielu miejscach!**

---

### Pełna hierarchia: nginx → Uvicorn → Starlette → FastAPI

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/users")
async def get_users():
    return [{"id": 1, "name": "John"}]
```

**Co się dzieje:**

```
1. nginx (port 80) dostaje request:
   GET /users HTTP/1.1

   ↓ proxy_pass http://127.0.0.1:8000

2. Uvicorn (port 8000) - ASGI Server:
   - Przyjmuje HTTP request
   - Parsuje headers, body
   - Tworzy ASGI dict (environ)
   - Wywołuje app (FastAPI)

   ↓ calls FastAPI app

3. FastAPI:
   - Routing: GET /users → get_users()
   - Dependency injection
   - Pydantic validation (jeśli request body)
   - Wywołuje get_users()

   ↓ używa Starlette

4. Starlette (używane przez FastAPI):
   - Request object (starlette.requests.Request)
   - Response handling (starlette.responses.JSONResponse)
   - Middleware (CORS, etc.)
   - Routing (pod spodem)

   ↓ returns response

5. Uvicorn:
   - Konwertuje Python response → HTTP response
   - Wysyła do nginx

   ↓ proxy_pass response

6. nginx:
   - Wysyła response do klienta
```

**Starlette = warstwa między Uvicorn a FastAPI**

---

### Starlette vs Werkzeug vs Django core

**Analogia:**

| Framework | Low-level toolkit | Relationship |
|-----------|-------------------|--------------|
| **Flask** | Werkzeug (WSGI toolkit) | Flask zbudowany NA Werkzeug |
| **Django** | Django core (własny) | Django ma własny core |
| **FastAPI** | Starlette (ASGI framework) | FastAPI zbudowany NA Starlette |

**Starlette = Werkzeug dla ASGI**

---

### Czy trzeba znać Starlette żeby używać FastAPI?

**NIE, ale warto wiedzieć że istnieje!**

**Kiedy MUSISZ wiedzieć o Starlette:**

1. **Custom middleware:**
   ```python
   from starlette.middleware.base import BaseHTTPMiddleware

   class CustomMiddleware(BaseHTTPMiddleware):
       async def dispatch(self, request, call_next):
           # Custom logic
           response = await call_next(request)
           return response
   ```

2. **Advanced Request/Response:**
   ```python
   from fastapi import Request
   from starlette.responses import StreamingResponse

   @app.get("/stream")
   async def stream(request: Request):
       async def generate():
           for i in range(10):
               yield f"data: {i}\n\n"

       return StreamingResponse(generate(), media_type="text/event-stream")
   ```

3. **WebSockets:**
   ```python
   from fastapi import WebSocket

   @app.websocket("/ws")
   async def websocket_endpoint(websocket: WebSocket):
       # Starlette WebSocket API
       await websocket.accept()
   ```

4. **Testing:**
   ```python
   from fastapi.testclient import TestClient  # ← Uses Starlette TestClient!

   client = TestClient(app)
   response = client.get("/users")
   ```

**W 90% przypadków używasz FastAPI i nie myślisz o Starlette!**

---

### Kiedy używać czystego Starlette (bez FastAPI)?

✅ **Użyj Starlette gdy:**
- Potrzebujesz ultra-lightweight framework
- Nie potrzebujesz walidacji/OpenAPI
- Masz własny system walidacji
- Performance > convenience (marginalnie szybszy)
- Micro-service z jednym endpointem

❌ **Użyj FastAPI gdy:**
- API z wieloma endpointami
- Potrzebujesz walidacji (prawie zawsze!)
- Chcesz OpenAPI docs
- Potrzebujesz dependency injection
- **Default choice dla REST API!**

**FastAPI overhead jest MINIMALNY** - prawie zawsze lepiej użyć FastAPI!

---

### Benchmarki: Starlette vs FastAPI

```python
# Benchmark (requests/sec):

Pure Starlette:  ~25,000 req/s
FastAPI:         ~22,000 req/s  (12% wolniejsze)

Różnica: MARGINALNA!
FastAPI features: OGROMNE!

Verdict: Użyj FastAPI (warto stracić 12% dla DX)
```

**FastAPI overhead = minimalny, features = ogromne!**

---

### FastAPI source code - używa Starlette

```python
# FastAPI source (uproszczone)
from starlette.applications import Starlette
from starlette.routing import Route

class FastAPI(Starlette):  # ← FastAPI INHERITS from Starlette!
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # FastAPI dodaje:
        self.openapi_schema = None  # OpenAPI spec
        self.dependency_overrides = {}  # DI overrides
        # etc.

    def get(self, path, **kwargs):
        # FastAPI decorator używa Starlette routing pod spodem
        def decorator(func):
            route = Route(path, func, methods=["GET"])
            self.routes.append(route)  # Starlette routes!
            return func
        return decorator
```

**FastAPI = Starlette subclass + Pydantic + extras**

---

### Ekosystem Starlette

**Inne frameworki zbudowane na Starlette:**

1. **FastAPI** - full-featured REST API framework
2. **Responder** - Flask-like framework (Kenneth Reitz)
3. **Bocadillo** - async web framework
4. **Starlite** - competitor dla FastAPI (teraz "Litestar")

**Starlette = fundament dla wielu ASGI frameworków**

---

### Podsumowanie - Gdzie Starlette w ekosystemie:

```
┌─────────────────────────────────────────────────────┐
│                   nginx (HTTP Server)                │
│           - Static files, SSL, reverse proxy         │
└────────────────────┬────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────┐
│          Gunicorn (Process Manager)                  │
│              - Fork workers, health checks           │
└────────────────────┬────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────┐
│   Uvicorn Worker (ASGI Server - implementuje ASGI)  │
│   - Event loop, HTTP parsing                        │
│   - Mapuje HTTP → Python callable (standard ASGI)   │
└────────────────────┬────────────────────────────────┘
                     │ uruchamia aplikację Python
                     ↓
┌─────────────────────────────────────────────────────┐
│                  Python Process                      │
│                                                      │
│       ┌─────────────────────────────────┐           │
│       │  FastAPI (High-level Framework) │           │
│       │  - Pydantic validation          │           │
│       │  - Dependency Injection         │           │
│       │  - OpenAPI/Swagger docs         │           │
│       │  - Type hints → validation      │           │
│       └──────────────┬──────────────────┘           │
│                      │ zbudowane NA                 │
│                      ↓                               │
│       ┌─────────────────────────────────┐           │
│       │  Starlette (Low-level toolkit)  │           │
│       │  - Routing                      │           │
│       │  - Request/Response             │           │
│       │  - Middleware                   │           │
│       │  - WebSockets                   │           │
│       │  - Background tasks             │           │
│       └─────────────────────────────────┘           │
│                                                      │
└─────────────────────────────────────────────────────┘

ASGI = Standard mówiący JAK Uvicorn ma komunikować się z aplikacją
       (nie jest warstwą w architekturze!)
```

**Kluczowe:**
- **ASGI** = standard/protokół (specyfikacja HTTP → Python callable)
- **Uvicorn** = ASGI server (implementuje standard ASGI)
- **Starlette** = ASGI framework/toolkit (narzędzia do budowania ASGI apps)
- **FastAPI** = high-level framework (zbudowany NA Starlette)
- **Gunicorn** = process manager
- **nginx** = HTTP server + reverse proxy

**Starlette = toolkit który FastAPI używa do obsługi requestów**

---

### Analogia finalna:

```
Tankowiec = nginx (transport HTTP, reverse proxy)
  ↓ dostarcza requesty
Stacja benzynowa = Uvicorn (przetwarza HTTP → Python, implementuje standard ASGI)
  ↓ uruchamia
Samochód = FastAPI (full-featured, wygodny)
  ↓ zbudowany na
Silnik + Przekładnia = Starlette (core toolkit, podstawa)

ASGI = Instrukcja obsługi (standard mówiący JAK stacja benzynowa ma tankować samochód)
```

**Poprawne zrozumienie:**
- **Uvicorn** = implementuje instrukcję obsługi (ASGI standard)
- **Starlette** = silnik na którym zbudowany jest FastAPI

---

### Najważniejsze do zapamiętania:

1. **Starlette = low-level ASGI framework** (jak Werkzeug dla WSGI)
2. **FastAPI zbudowane NA Starlette** (używa Starlette jako fundamentu)
3. **Starlette = routing, requests, responses, middleware, WebSockets**
4. **FastAPI dodaje: Pydantic, DI, OpenAPI, auto-validation**
5. **Hierarchia: nginx → Uvicorn → Starlette → FastAPI**
6. **Nie musisz znać Starlette żeby używać FastAPI** (ale warto wiedzieć!)
7. **Starlette używane przez FastAPI:** Request/Response, middleware, WebSockets
8. **Default: Użyj FastAPI** (overhead minimalny, features ogromne)

**Starlette to "ukryty bohater" FastAPI!**

---
## 15. Co się dzieje krok po kroku: `runserver`, `flask run`, `fastapi dev`

**Pytanie:** Co dokładnie się uruchamia gdy robię `python manage.py runserver` (Django), `flask run` (Flask), czy `fastapi dev` (FastAPI)? Jaki serwer HTTP, jaki serwer WSGI/ASGI, jak to wszystko się łączy?

**Odpowiedź:**

Świetne pytanie! To jest klucz do zrozumienia development servers. Zobaczmy **dokładnie krok po kroku** co się dzieje w każdym przypadku.

---

## 📦 TL;DR - Szybkie podsumowanie:

```
Django runserver:
  Uruchamia: Django dev server (wsgiref z Python stdlib)
  Stack: HTTP Server + WSGI Server + Django app (wszystko w jednym procesie)

Flask run:
  Uruchamia: Werkzeug dev server
  Stack: HTTP Server + WSGI Server + Flask app (wszystko w jednym procesie)

FastAPI dev:
  Uruchamia: Uvicorn dev server
  Stack: HTTP Server + ASGI Server + FastAPI app (wszystko w jednym procesie)
```

**Kluczowe:** Development servers łączą HTTP Server + WSGI/ASGI Server + Application w **jeden proces** dla wygody developmentu!

---

## 🔵 Django: `python manage.py runserver`

### Co się uruchamia:

```
┌─────────────────────────────────────────────────────┐
│          JEDEN PROCES (development)                  │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  HTTP Server (wsgiref.simple_server)       │    │
│  │  - Słucha na porcie 8000                   │    │
│  │  - Parsuje HTTP requesty                   │    │
│  └──────────────┬─────────────────────────────┘    │
│                 │                                    │
│                 ↓                                    │
│  ┌────────────────────────────────────────────┐    │
│  │  WSGI Server (ServerHandler z wsgiref)     │    │
│  │  - Implementuje standard WSGI              │    │
│  │  - Mapuje HTTP → Python callable           │    │
│  └──────────────┬─────────────────────────────┘    │
│                 │                                    │
│                 ↓ wywołuje aplikację WSGI           │
│  ┌────────────────────────────────────────────┐    │
│  │  Django Application                        │    │
│  │  - URLconf (routing)                       │    │
│  │  - Views                                   │    │
│  │  - Middleware                              │    │
│  │  - ORM                                     │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Krok po kroku:

**1. Uruchamiasz:**
```bash
python manage.py runserver
```

**2. Django wywołuje:**
```python
# django/core/management/commands/runserver.py
from django.core.servers.basehttp import run

# Uruchamia development server
run(
    addr='127.0.0.1',
    port=8000,
    wsgi_handler=get_internal_wsgi_application(),  # Twoja Django app jako WSGI callable
    ...
)
```

**3. Django uruchamia `wsgiref.simple_server`:**
```python
# django/core/servers/basehttp.py
from wsgiref import simple_server

class ServerHandler(simple_server.ServerHandler):
    # Django customization
    ...

# Tworzy HTTP server
httpd = simple_server.WSGIServer(
    server_address=('127.0.0.1', 8000),
    RequestHandlerClass=WSGIRequestHandler,
)

# Ustawia WSGI application (Twoja Django app)
httpd.set_app(wsgi_handler)

# Start serwera (słucha na porcie 8000)
httpd.serve_forever()
```

**4. Przychodzi request:**
```
Klient → http://127.0.0.1:8000/api/users/
```

**5. Flow przez stack:**

```
┌─────────────────────────────────────────────┐
│ 1. HTTP Server (wsgiref)                    │
│    - Odbiera raw HTTP request               │
│    - Parsuje: method, path, headers, body   │
│    - Tworzy environ dict (WSGI)             │
└─────────────┬───────────────────────────────┘
              │
              ↓ environ = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/api/users/', ...}
┌─────────────────────────────────────────────┐
│ 2. WSGI Server (ServerHandler)              │
│    - Wywołuje: response = app(environ, start_response) │
│    - Przekazuje request do Django           │
└─────────────┬───────────────────────────────┘
              │
              ↓ wywołuje Django WSGI callable
┌─────────────────────────────────────────────┐
│ 3. Django Application                       │
│    a) Middleware (request processing)       │
│    b) URLconf (routing: /api/users/ → view) │
│    c) View function (business logic)        │
│    d) Response creation                     │
│    e) Middleware (response processing)      │
└─────────────┬───────────────────────────────┘
              │
              ↓ zwraca WSGI response
┌─────────────────────────────────────────────┐
│ 4. WSGI Server                              │
│    - Otrzymuje response (status, headers, body) │
│    - Konwertuje do HTTP response            │
└─────────────┬───────────────────────────────┘
              │
              ↓ HTTP/1.1 200 OK...
┌─────────────────────────────────────────────┐
│ 5. HTTP Server                              │
│    - Wysyła HTTP response do klienta        │
└─────────────────────────────────────────────┘
```

### Szczegóły techniczne:

```python
# Co Django używa pod spodem:

# 1. HTTP Server
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
# Prosty HTTP/1.0 server z Python stdlib
# TYLKO do development (single-threaded, brak SSL, etc.)

# 2. WSGI Server
from wsgiref.simple_server import ServerHandler
# Implementacja standardu WSGI (PEP 3333)
# Tłumaczy HTTP → WSGI environ dict

# 3. Django WSGI Application
def get_wsgi_application():
    django.setup()
    return WSGIHandler()  # Django callable spełniające WSGI spec

class WSGIHandler:
    def __call__(self, environ, start_response):
        # Django routing, views, middleware, etc.
        ...
        return response
```

### Co Django NIE używa:

❌ **Werkzeug** (to Flask)
❌ **Uvicorn** (to ASGI)
❌ **Gunicorn** (to production)
❌ **nginx** (to production)

✅ **Django używa:** `wsgiref` z Python standard library (prosty, ale wystarczający do dev)

---

## 🟢 Flask: `flask run`

### Co się uruchamia:

```
┌─────────────────────────────────────────────────────┐
│          JEDEN PROCES (development)                  │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  HTTP Server (Werkzeug)                    │    │
│  │  - Słucha na porcie 5000                   │    │
│  │  - Parsuje HTTP requesty                   │    │
│  │  - Obsługuje keep-alive, chunked, etc.     │    │
│  └──────────────┬─────────────────────────────┘    │
│                 │                                    │
│                 ↓                                    │
│  ┌────────────────────────────────────────────┐    │
│  │  WSGI Server (Werkzeug)                    │    │
│  │  - Implementuje standard WSGI              │    │
│  │  - Mapuje HTTP → Python callable           │    │
│  └──────────────┬─────────────────────────────┘    │
│                 │                                    │
│                 ↓ wywołuje aplikację WSGI           │
│  ┌────────────────────────────────────────────┐    │
│  │  Flask Application                         │    │
│  │  - Routing (@app.route)                    │    │
│  │  - Views                                   │    │
│  │  - Extensions                              │    │
│  │  - Request/Response (Werkzeug!)            │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Krok po kroku:

**1. Uruchamiasz:**
```bash
flask run
# lub: python -m flask run
```

**2. Flask CLI wywołuje:**
```python
# flask/cli.py
from werkzeug.serving import run_simple

@click.command('run')
def run_command():
    # Pobiera Flask app
    app = locate_app()  # Twoja Flask app

    # Uruchamia Werkzeug dev server
    run_simple(
        hostname='127.0.0.1',
        port=5000,
        application=app,  # Twoja Flask app jako WSGI callable
        use_reloader=True,
        use_debugger=True,
    )
```

**3. Werkzeug uruchamia HTTP server:**
```python
# werkzeug/serving.py
from http.server import HTTPServer, BaseHTTPRequestHandler

def run_simple(hostname, port, application, ...):
    # Tworzy HTTP server
    srv = make_server(
        host=hostname,
        port=port,
        app=application,  # WSGI callable
        threaded=True,    # Multi-threaded (lepsze niż wsgiref!)
        ...
    )

    # Start serwera
    srv.serve_forever()

def make_server(host, port, app, threaded=False, ...):
    # Werkzeug's custom HTTP server
    class WSGIRequestHandler(BaseHTTPRequestHandler):
        def handle(self):
            # Custom HTTP parsing (lepsze niż stdlib)
            ...
            # Wywołuje WSGI app
            response = self.server.app(environ, start_response)
            ...

    return HTTPServer((host, port), WSGIRequestHandler)
```

**4. Przychodzi request:**
```
Klient → http://127.0.0.1:5000/api/users
```

**5. Flow przez stack:**

```
┌─────────────────────────────────────────────┐
│ 1. HTTP Server (Werkzeug)                   │
│    - Odbiera raw HTTP request               │
│    - Parsuje: method, path, headers, body   │
│    - Tworzy environ dict (WSGI)             │
│    - Obsługuje HTTP/1.1 features            │
└─────────────┬───────────────────────────────┘
              │
              ↓ environ = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/api/users', ...}
┌─────────────────────────────────────────────┐
│ 2. WSGI Server (Werkzeug)                   │
│    - Wywołuje: response = app(environ, start_response) │
│    - Przekazuje request do Flask            │
└─────────────┬───────────────────────────────┘
              │
              ↓ wywołuje Flask WSGI callable
┌─────────────────────────────────────────────┐
│ 3. Flask Application                        │
│    a) Request object creation (Werkzeug)    │
│    b) Routing (/api/users → view function)  │
│    c) View function (business logic)        │
│    d) Response creation (Werkzeug)          │
└─────────────┬───────────────────────────────┘
              │
              ↓ zwraca WSGI response
┌─────────────────────────────────────────────┐
│ 4. WSGI Server (Werkzeug)                   │
│    - Otrzymuje response (status, headers, body) │
│    - Konwertuje do HTTP response            │
└─────────────┬───────────────────────────────┘
              │
              ↓ HTTP/1.1 200 OK...
┌─────────────────────────────────────────────┐
│ 5. HTTP Server (Werkzeug)                   │
│    - Wysyła HTTP response do klienta        │
└─────────────────────────────────────────────┘
```

### Szczegóły techniczne:

```python
# Co Flask używa pod spodem:

# 1. HTTP Server + WSGI Server (Werkzeug)
from werkzeug.serving import run_simple
# Werkzeug to wszystko-w-jednym:
# - HTTP server (lepszy niż wsgiref)
# - WSGI server (implementuje WSGI spec)
# - Request/Response classes
# - Routing utilities
# - Debugging tools

# 2. Flask Application
class Flask:
    def __call__(self, environ, start_response):
        # Flask routing, views, etc.
        # Używa Werkzeug Request/Response
        ...
        return response

    def wsgi_app(self, environ, start_response):
        ctx = self.request_context(environ)
        response = self.full_dispatch_request()
        return response(environ, start_response)
```

### Kluczowe różnice vs Django:

| Aspekt | Django | Flask |
|--------|--------|-------|
| **HTTP Server** | wsgiref (stdlib) | Werkzeug (custom) |
| **Threading** | Single-threaded | Multi-threaded (default) |
| **HTTP/1.1** | Podstawowy | Pełny support |
| **Auto-reload** | Tak | Tak |
| **Debugger** | Basic | Werkzeug debugger (lepszy!) |
| **Request/Response** | Django custom | Werkzeug classes |

### Co Flask NIE używa:

❌ **wsgiref** (Django używa)
❌ **Uvicorn** (to ASGI)
❌ **Gunicorn** (to production)
❌ **nginx** (to production)

✅ **Flask używa:** Werkzeug (lepszy dev server niż wsgiref, ale dalej tylko do dev!)

---

## 🔴 FastAPI: `fastapi dev`

### Co się uruchamia:

```
┌─────────────────────────────────────────────────────┐
│          JEDEN PROCES (development)                  │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  HTTP Server (Uvicorn)                     │    │
│  │  - Słucha na porcie 8000                   │    │
│  │  - Parsuje HTTP requesty (httptools/h11)   │    │
│  │  - WebSocket support                       │    │
│  └──────────────┬─────────────────────────────┘    │
│                 │                                    │
│                 ↓                                    │
│  ┌────────────────────────────────────────────┐    │
│  │  ASGI Server (Uvicorn)                     │    │
│  │  - Implementuje standard ASGI              │    │
│  │  - Event loop (asyncio/uvloop)             │    │
│  │  - Mapuje HTTP → Python async callable     │    │
│  └──────────────┬─────────────────────────────┘    │
│                 │                                    │
│                 ↓ await app(scope, receive, send)   │
│  ┌────────────────────────────────────────────┐    │
│  │  FastAPI + Starlette                       │    │
│  │                                            │    │
│  │  FastAPI layer:                            │    │
│  │  - Pydantic validation                     │    │
│  │  - Dependency Injection                    │    │
│  │  - OpenAPI docs                            │    │
│  │                                            │    │
│  │  Starlette layer (core):                   │    │
│  │  - Routing                                 │    │
│  │  - Request/Response                        │    │
│  │  - Middleware                              │    │
│  │  - WebSockets                              │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Krok po kroku:

**1. Uruchamiasz:**
```bash
fastapi dev main.py
# lub: uvicorn main:app --reload
```

**2. FastAPI CLI (lub Uvicorn) wywołuje:**
```python
# fastapi/cli.py (wrapper wokół Uvicorn)
import uvicorn

@click.command('dev')
def dev_command(path: str):
    # Znajduje FastAPI app w pliku
    app = f"{module}:{app_name}"  # np. "main:app"

    # Uruchamia Uvicorn
    uvicorn.run(
        app="main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Auto-reload on file changes
        log_level="info",
    )
```

**3. Uvicorn uruchamia async HTTP server:**
```python
# uvicorn/main.py
import asyncio

class Server:
    def run(self):
        # Tworzy event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Tworzy async HTTP server
        config = Config(
            app=self.app,  # FastAPI app (ASGI callable)
            host="127.0.0.1",
            port=8000,
            loop="auto",  # uvloop jeśli dostępny
        )

        server = ServerState(config)

        # Start async server
        loop.run_until_complete(server.serve())

# uvicorn/protocols/http/httptools_impl.py
class HttpToolsProtocol(asyncio.Protocol):
    # Async HTTP protocol
    # Używa httptools (C binding do nodejs http-parser)

    def on_message_complete(self):
        # Otrzymał pełny HTTP request
        # Tworzy ASGI scope dict
        scope = {
            'type': 'http',
            'method': self.method,
            'path': self.path,
            ...
        }

        # Wywołuje ASGI app (async!)
        task = self.loop.create_task(
            self.app(scope, self.receive, self.send)
        )
```

**4. Przychodzi request:**
```
Klient → http://127.0.0.1:8000/api/users
```

**5. Flow przez stack (ASYNC!):**

```
┌─────────────────────────────────────────────┐
│ 1. HTTP Server (Uvicorn - async)            │
│    - Odbiera raw HTTP request               │
│    - Parsuje: method, path, headers, body   │
│    - Tworzy scope dict (ASGI)               │
└─────────────┬───────────────────────────────┘
              │
              ↓ scope = {'type': 'http', 'method': 'GET', 'path': '/api/users', ...}
┌─────────────────────────────────────────────┐
│ 2. ASGI Server (Uvicorn - event loop)       │
│    - await app(scope, receive, send)        │
│    - Przekazuje request do FastAPI          │
└─────────────┬───────────────────────────────┘
              │
              ↓ async call
┌─────────────────────────────────────────────┐
│ 3. Starlette (ASGI routing/middleware)      │
│    - Routing (/api/users → endpoint)        │
│    - Middleware (CORS, etc.)                │
│    - Request object creation                │
└─────────────┬───────────────────────────────┘
              │
              ↓ async call
┌─────────────────────────────────────────────┐
│ 4. FastAPI (dependency injection + validation) │
│    - Dependency injection                   │
│    - Pydantic validation                    │
│    - Wywołuje endpoint function             │
└─────────────┬───────────────────────────────┘
              │
              ↓ async endpoint
┌─────────────────────────────────────────────┐
│ 5. Your Endpoint Function                   │
│    async def get_users():                   │
│        users = await db.fetch_all(...)  ← async I/O! │
│        return users                         │
└─────────────┬───────────────────────────────┘
              │
              ↓ returns data
┌─────────────────────────────────────────────┐
│ 6. FastAPI (serialization)                  │
│    - Pydantic serialization                 │
│    - JSON response creation                 │
└─────────────┬───────────────────────────────┘
              │
              ↓ Starlette Response
┌─────────────────────────────────────────────┐
│ 7. Starlette (response processing)          │
│    - Response middleware                    │
│    - Headers, cookies, etc.                 │
└─────────────┬───────────────────────────────┘
              │
              ↓ async send()
┌─────────────────────────────────────────────┐
│ 8. ASGI Server (Uvicorn)                    │
│    - Otrzymuje response via send()          │
│    - Konwertuje do HTTP response            │
└─────────────┬───────────────────────────────┘
              │
              ↓ HTTP/1.1 200 OK...
┌─────────────────────────────────────────────┐
│ 9. HTTP Server (Uvicorn)                    │
│    - Wysyła HTTP response do klienta        │
└─────────────────────────────────────────────┘
```

### Szczegóły techniczne:

```python
# Co FastAPI używa pod spodem:

# 1. HTTP Server (Uvicorn - async)
import uvicorn
import asyncio
import httptools  # C binding do nodejs http-parser (szybki!)
# lub: import h11  # Pure-Python HTTP/1.1 parser (fallback)

# Event loop:
try:
    import uvloop  # Szybszy event loop (C)
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass  # Fallback do asyncio

# 2. ASGI Server (Uvicorn)
# Implementuje ASGI spec (async callable)
async def app(scope, receive, send):
    # scope = request metadata
    # receive = async callable do otrzymywania body
    # send = async callable do wysyłania response
    ...

# 3. FastAPI + Starlette Application
from fastapi import FastAPI
from starlette.applications import Starlette

class FastAPI(Starlette):  # FastAPI inherits from Starlette!
    def __init__(self):
        super().__init__()
        # FastAPI additions: Pydantic, DI, OpenAPI
        ...

    async def __call__(self, scope, receive, send):
        # ASGI callable
        # Starlette routing + middleware
        # FastAPI validation + DI
        ...
```

### Kluczowe różnice vs Django/Flask:

| Aspekt | Django | Flask | FastAPI |
|--------|--------|-------|---------|
| **Standard** | WSGI | WSGI | **ASGI** |
| **Server** | wsgiref | Werkzeug | **Uvicorn** |
| **Async** | ❌ Nie | ❌ Nie | ✅ **TAK** |
| **Event loop** | ❌ | ❌ | ✅ asyncio/uvloop |
| **WebSockets** | ❌ (wymaga Channels) | ❌ (wymaga extensionów) | ✅ Built-in |
| **HTTP Parser** | stdlib | Werkzeug | **httptools (C)** |
| **Threading** | Single | Multi | **Event loop (async)** |
| **I/O** | Blocking | Blocking | **Non-blocking** |

### Co FastAPI NIE używa:

❌ **wsgiref** (Django używa)
❌ **Werkzeug** (Flask używa)
❌ **Gunicorn** (to production - choć może używać Uvicorn workers!)
❌ **nginx** (to production)

✅ **FastAPI używa:** Uvicorn (ASGI server, async, szybki!)

---

## 📊 Porównanie side-by-side:

```
┌──────────────────────────────────────────────────────────────────┐
│                    DJANGO RUNSERVER                              │
├──────────────────────────────────────────────────────────────────┤
│ Command:  python manage.py runserver                            │
│ Port:     8000 (default)                                         │
│ Technologia:                                                     │
│   - HTTP Server:  wsgiref.simple_server (Python stdlib)         │
│   - WSGI Server:  ServerHandler (wsgiref)                       │
│   - Framework:    Django (monolit)                              │
│ Features:                                                        │
│   ✅ Auto-reload                                                 │
│   ✅ Static files serving                                        │
│   ❌ Multi-threading (single-threaded!)                          │
│   ❌ Production-ready                                            │
│ Stack: wsgiref → WSGI → Django                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      FLASK RUN                                   │
├──────────────────────────────────────────────────────────────────┤
│ Command:  flask run                                             │
│ Port:     5000 (default)                                         │
│ Technologia:                                                     │
│   - HTTP Server:  Werkzeug (custom HTTP server)                 │
│   - WSGI Server:  Werkzeug (WSGI implementation)                │
│   - Framework:    Flask (zbudowany NA Werkzeug)                 │
│ Features:                                                        │
│   ✅ Auto-reload                                                 │
│   ✅ Interactive debugger (Werkzeug)                             │
│   ✅ Multi-threading (default: threaded=True)                    │
│   ✅ Better HTTP/1.1 support                                     │
│   ❌ Production-ready                                            │
│ Stack: Werkzeug → WSGI → Flask                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    FASTAPI DEV                                   │
├──────────────────────────────────────────────────────────────────┤
│ Command:  fastapi dev main.py  (lub: uvicorn main:app --reload) │
│ Port:     8000 (default)                                         │
│ Technologia:                                                     │
│   - HTTP Server:  Uvicorn (async HTTP server)                   │
│   - ASGI Server:  Uvicorn (ASGI implementation)                 │
│   - Framework:    FastAPI (zbudowany NA Starlette)              │
│ Features:                                                        │
│   ✅ Auto-reload                                                 │
│   ✅ Async/await support                                         │
│   ✅ WebSockets                                                  │
│   ✅ HTTP/2 (z hypercorn)                                        │
│   ✅ Event loop (asyncio/uvloop)                                 │
│   ✅ Non-blocking I/O                                            │
│   ❌ Production-ready (wymaga Gunicorn + Uvicorn workers)        │
│ Stack: Uvicorn → ASGI → Starlette → FastAPI                     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Kluczowe wnioski:

### 1. Development servers to wszystko-w-jednym:

```
Production (osobne komponenty):
  nginx (HTTP Server)
    ↓
  Gunicorn (Process Manager)
    ↓
  Uvicorn Worker (ASGI Server)
    ↓
  FastAPI (Application)

Development (jeden proces):
  Uvicorn (HTTP + ASGI + FastAPI w jednym procesie)
```

### 2. Każdy framework ma swój dev server:

| Framework | Dev Server | Bazuje na |
|-----------|------------|-----------|
| Django | django.core.servers | **wsgiref** (Python stdlib) |
| Flask | Werkzeug dev server | **Werkzeug** (custom) |
| FastAPI | Uvicorn | **Uvicorn** (async) |

### 3. Framework != Server:

```
❌ BŁĘDNE myślenie:
"Django to serwer HTTP"

✅ POPRAWNE myślenie:
"Django to framework. Dla dev używa wsgiref. Dla production używam Gunicorn."
```

### 4. WSGI vs ASGI flow:

```
WSGI (Django, Flask):
  HTTP Request → WSGI Server → app(environ, start_response) → Response
  ↑ Synchroniczne (blocking I/O)

ASGI (FastAPI):
  HTTP Request → ASGI Server → await app(scope, receive, send) → Response
  ↑ Asynchroniczne (non-blocking I/O)
```

### 5. Production NIE używa development servers:

```
❌ NIGDY w production:
  - python manage.py runserver
  - flask run
  - uvicorn main:app (bez Gunicorn)

✅ Production:
  - Gunicorn/uWSGI (WSGI)
  - Gunicorn + Uvicorn workers (ASGI)
  - nginx (reverse proxy, SSL, static files)
```

---

## 🎯 Analogia finalna:

### Development (restauracja domowa):

```
Django runserver = Jeden kucharz (wsgiref) robi wszystko
  - Przyjmuje zamówienia (HTTP)
  - Gotuje (WSGI)
  - Serwuje (Django app)
  - Powolny, ale wystarczy do testowania

Flask run = Lepszy kucharz (Werkzeug) robi wszystko
  - Przyjmuje zamówienia (HTTP)
  - Gotuje (WSGI)
  - Serwuje (Flask app)
  - Może obsłużyć kilka osób jednocześnie (multi-threaded)

FastAPI dev = Nowoczesny kucharz (Uvicorn) robi wszystko async
  - Przyjmuje zamówienia (HTTP)
  - Gotuje asynchronicznie (ASGI)
  - Serwuje (FastAPI app)
  - Może robić wiele rzeczy jednocześnie (event loop)
```

### Production (restauracja komercyjna):

```
nginx = Recepcjonista (przyjmuje gości, prowadzi do stolików)
  ↓
Gunicorn = Manager (zarządza kucharzami, health checks)
  ↓
Uvicorn Workers = Kucharze (każdy gotuje asynchronicznie)
  ↓
FastAPI = Przepisy (Twój kod)
```

---

## 💡 Najważniejsze do zapamiętania:

1. **Development servers łączą HTTP + WSGI/ASGI + Application** w jeden proces
2. **Django używa wsgiref** (Python stdlib, basic ale wystarczający)
3. **Flask używa Werkzeug** (lepszy dev server, multi-threaded)
4. **FastAPI używa Uvicorn** (async, event loop, WebSockets)
5. **WSZYSCY używają różnych serwerów w production** (Gunicorn + nginx)
6. **Framework ≠ Server** - to są różne rzeczy!
7. **Development servers są TYLKO do developmentu** - nigdy production!

---

**Teraz wiesz dokładnie co się uruchamia gdy robisz `runserver`, `flask run`, czy `fastapi dev`!** 🚀

---

## 16. Czy Uvicorn jest domyślny w FastAPI? Co jeśli go odinstaluję?

**Pytanie:** Czy Uvicorn jest domyślny we FastAPI? Jeśli odinstaluję Uvicorn, to `fastapi dev` przestanie działać?

**Odpowiedź:**

**TAK**, jeśli odinstalujesz Uvicorn, `fastapi dev` przestanie działać. **Ale** - to zależy jak zainstalowałeś FastAPI!

To jest **KLUCZOWA różnica** między FastAPI a Django/Flask:

---

## 🔑 Kluczowa różnica: FastAPI NIE ma wbudowanego serwera!

```
┌─────────────────────────────────────────────────────┐
│ Django                                              │
│ - Framework MA wbudowany dev server (wsgiref)       │
│ - pip install django → działa python manage.py runserver │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Flask                                               │
│ - Framework MA wbudowany dev server (Werkzeug)      │
│ - pip install flask → działa flask run             │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ FastAPI                                             │
│ - Framework NIE MA wbudowanego dev serwera!         │
│ - pip install fastapi → NIE DZIAŁA fastapi dev      │
│ - Musisz OSOBNO zainstalować ASGI server (Uvicorn)  │
└─────────────────────────────────────────────────────┘
```

**FastAPI = tylko framework (routing, validation, DI, OpenAPI)**

**Uvicorn = ASGI server (potrzebny do uruchomienia FastAPI)**

---

## 📦 Instalacja FastAPI - dwie opcje:

### Opcja 1: Minimalna (tylko framework)

```bash
pip install fastapi
```

**Co dostajesz:**
- ✅ FastAPI framework (routing, Pydantic validation, DI, OpenAPI)
- ✅ Starlette (core toolkit)
- ✅ Pydantic (validation)
- ❌ **BRAK Uvicorn** (nie możesz uruchomić aplikacji!)
- ❌ BRAK innych optional dependencies

**Próba uruchomienia:**
```bash
fastapi dev main.py
# ❌ ERROR: No module named 'uvicorn'

uvicorn main:app
# ❌ ERROR: No module named 'uvicorn'
```

**Do czego to służy:**
- Kiedy chcesz użyć innego ASGI serwera (Hypercorn, Daphne)
- Kiedy instalujesz FastAPI jako dependency w większym projekcie
- Kiedy chcesz minimalną instalację (np. w Dockerze)

---

### Opcja 2: Standard (framework + Uvicorn + extras)

```bash
pip install "fastapi[standard]"
# lub (stara wersja):
pip install "fastapi[all]"
```

**Co dostajesz:**
- ✅ FastAPI framework
- ✅ Starlette
- ✅ Pydantic
- ✅ **Uvicorn** (ASGI server + HTTP parser)
- ✅ `python-multipart` (file uploads)
- ✅ `email-validator` (email validation)
- ✅ `jinja2` (templating)
- ✅ `httpx` (test client)
- ✅ i inne...

**Próba uruchomienia:**
```bash
fastapi dev main.py
# ✅ Działa! (uruchamia Uvicorn)

uvicorn main:app --reload
# ✅ Działa!
```

**Do czego to służy:**
- **Development** (recommended!)
- Dostajesz wszystko co potrzebujesz od razu
- Najwygodniejsze dla początkujących

---

## ❌ Co się stanie jak odinstaluję Uvicorn?

### Test:

```bash
# Masz zainstalowane: fastapi + uvicorn
pip uninstall uvicorn

# Próba uruchomienia:
fastapi dev main.py
```

**Wynik:**
```
❌ ERROR: No module named 'uvicorn'
```

### Dlaczego?

`fastapi dev` to **wrapper wokół Uvicorn**:

```python
# fastapi/cli.py (uproszczone)
import uvicorn

def dev_command(path: str):
    # FastAPI CLI po prostu wywołuje Uvicorn!
    uvicorn.run(
        app="main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
```

**Bez Uvicorn, `fastapi dev` nie może działać!**

---

## 🔄 Czy mogę użyć innego serwera zamiast Uvicorn?

**TAK!** FastAPI to **ASGI framework** - możesz użyć dowolnego ASGI serwera:

### Opcja 1: Uvicorn (recommended)

```bash
pip install uvicorn[standard]
uvicorn main:app --reload
```

**Dlaczego Uvicorn:**
- ✅ Szybki (httptools, uvloop)
- ✅ Prosty w użyciu
- ✅ Najpopularniejszy dla FastAPI
- ✅ `fastapi dev` działa out-of-the-box

---

### Opcja 2: Hypercorn

```bash
pip install hypercorn
hypercorn main:app --reload
```

**Dlaczego Hypercorn:**
- ✅ Obsługuje HTTP/2 (Uvicorn nie obsługuje)
- ✅ Obsługuje HTTP/3 (QUIC)
- ✅ Trio support (alternatywa dla asyncio)
- ❌ Wolniejszy niż Uvicorn (pure-Python HTTP parser)

---

### Opcja 3: Daphne

```bash
pip install daphne
daphne main:app
```

**Dlaczego Daphne:**
- ✅ Stworzony dla Django Channels
- ✅ WebSockets support
- ❌ Wolniejszy niż Uvicorn
- ❌ Mniej popularny dla FastAPI

---

### Opcja 4: Granian

```bash
pip install granian
granian --interface asgi main:app
```

**Dlaczego Granian:**
- ✅ Napisany w Rust (bardzo szybki!)
- ✅ Nowoczesny
- ❌ Nowy projekt (mniej mature)

---

## 📊 Porównanie: Django/Flask vs FastAPI

| Aspekt | Django | Flask | FastAPI |
|--------|--------|-------|---------|
| **Framework zawiera dev server?** | ✅ TAK (wsgiref) | ✅ TAK (Werkzeug) | ❌ **NIE** |
| **Domyślny dev server** | wsgiref (wbudowany) | Werkzeug (wbudowany) | **Brak (musisz zainstalować)** |
| **Minimalna instalacja** | `pip install django` → działa `runserver` | `pip install flask` → działa `flask run` | `pip install fastapi` → **NIE** działa `fastapi dev` |
| **Pełna instalacja** | - | - | `pip install "fastapi[standard]"` → działa `fastapi dev` |
| **Serwer do zainstalowania** | - (nie trzeba) | - (nie trzeba) | **Uvicorn (trzeba!)** |
| **Alternatywne serwery dev** | - | - | Hypercorn, Daphne, Granian |

---

## 💡 Kluczowe wnioski:

### 1. FastAPI ≠ Uvicorn

```
FastAPI = Framework (routing, validation, DI, OpenAPI)
  ↓ potrzebuje
Uvicorn = ASGI Server (uruchamia aplikację ASGI)
```

**To są DWIE OSOBNE BIBLIOTEKI!**

---

### 2. Django/Flask mają wbudowane dev servers, FastAPI NIE

```
Django:
  pip install django
  → django zawiera wsgiref
  → python manage.py runserver działa ✅

Flask:
  pip install flask
  → flask zawiera Werkzeug
  → flask run działa ✅

FastAPI:
  pip install fastapi
  → fastapi NIE zawiera serwera
  → fastapi dev main.py NIE działa ❌
  
  pip install "fastapi[standard]"
  → zawiera Uvicorn
  → fastapi dev main.py działa ✅
```

---

### 3. `fastapi dev` to wrapper wokół Uvicorn

```python
# Co robi `fastapi dev`:
import uvicorn

uvicorn.run(
    app="main:app",
    host="127.0.0.1",
    port=8000,
    reload=True,
)
```

**Bez Uvicorn, `fastapi dev` NIE MOŻE działać!**

---

### 4. Możesz użyć innego ASGI serwera

```bash
# Zamiast Uvicorn, możesz użyć:
pip install hypercorn
hypercorn main:app --reload

# Ale wtedy `fastapi dev` nie zadziała (wymaga Uvicorn)
# Musisz użyć komendy Hypercorn bezpośrednio
```

---

### 5. Zalecana instalacja dla developmentu:

```bash
# ✅ Recommended (dostaniesz Uvicorn + wszystko):
pip install "fastapi[standard]"

# ❌ Nie recommended dla początkujących (brak Uvicorn):
pip install fastapi
```

---

## 🎯 Analogia:

```
Django/Flask = Samochód z silnikiem (gotowy do jazdy)
  → pip install django
  → python manage.py runserver
  → Działa od razu! ✅

FastAPI = Nadwozie bez silnika
  → pip install fastapi
  → fastapi dev main.py
  → ERROR: No engine! ❌
  
  → pip install "fastapi[standard]"  (dodajesz silnik - Uvicorn)
  → fastapi dev main.py
  → Działa! ✅
```

---

## 📝 Podsumowanie:

1. **FastAPI NIE ma wbudowanego dev serwera** (w przeciwieństwie do Django/Flask)
2. **Uvicorn jest osobną biblioteką** (nie jest częścią FastAPI)
3. **`pip install fastapi`** = tylko framework (NIE zawiera Uvicorn)
4. **`pip install "fastapi[standard]"`** = framework + Uvicorn + extras (recommended!)
5. **Jeśli odinstalujesz Uvicorn, `fastapi dev` przestanie działać** ❌
6. **Możesz użyć innych ASGI serwerów** (Hypercorn, Daphne, Granian)
7. **W produkcji używasz: Gunicorn + Uvicorn workers** (nie sam Uvicorn!)

---

**WNIOSEK:** Uvicorn NIE jest "domyślny" w FastAPI - to osobna biblioteka którą musisz zainstalować! FastAPI to tylko framework bez wbudowanego serwera.

---

## 17. Kto kogo uruchamia: Uvicorn uruchamia FastAPI czy FastAPI uruchamia Uvicorn?

**Pytanie:** Jak uruchamiam `uvicorn main:app --reload` albo `hypercorn main:app --reload`, to skąd FastAPI/Starlette wiedzą, żeby NIE uruchomić domyślnej konfiguracji Uvicorn?

**Odpowiedź:**

To jest **BARDZO WAŻNE nieporozumienie**! Myślisz o tym **ODWROTNIE**!

---

## ❌ BŁĘDNE myślenie:

```
FastAPI uruchamia Uvicorn
  ↓
FastAPI "wie" że Uvicorn już jest uruchomiony
  ↓
FastAPI "decyduje" nie uruchamiać Uvicorn ponownie
```

**To jest CAŁKOWICIE błędne!**

---

## ✅ POPRAWNE myślenie:

```
Uvicorn uruchamia FastAPI
  ↓
Uvicorn importuje Twój kod (main.py)
  ↓
Uvicorn znajduje obiekt `app`
  ↓
Uvicorn WYWOŁUJE `app` jako funkcję (ASGI callable)
  ↓
FastAPI ODPOWIADA na wywołanie
```

**FastAPI NIE uruchamia Uvicorn! To Uvicorn uruchamia FastAPI!**

---

## 🔑 Kluczowa prawda:

### FastAPI = pasywny obiekt (ASGI callable)
### Uvicorn = aktywny proces (ASGI server)

```python
# main.py
from fastapi import FastAPI

app = FastAPI()  # To tylko obiekt Python!

@app.get("/users")
async def get_users():
    return {"users": []}

# app nie "robi" nic sam z siebie!
# app nie "uruchamia się" sam!
# app nie "wie" że istnieje Uvicorn!
```

**`app` to tylko obiekt który CZEKA aż ktoś go wywoła!**

---

## 📖 Co się dzieje krok po kroku: `uvicorn main:app --reload`

### Krok 1: Uruchamia się Uvicorn (główny proces)

```bash
$ uvicorn main:app --reload
```

```python
# uvicorn/main.py
import sys
import asyncio

# Uvicorn startuje jako główny proces
def main():
    # Uvicorn parsuje argumenty: "main:app"
    module_name = "main"  # nazwa pliku
    app_name = "app"       # nazwa zmiennej
    
    # Uvicorn tworzy event loop
    loop = asyncio.new_event_loop()
    
    # Uvicorn uruchamia serwer
    server = Server(config)
    loop.run_until_complete(server.serve())
```

**Uvicorn = główny proces. On kontroluje wszystko.**

---

### Krok 2: Uvicorn IMPORTUJE Twój kod

```python
# uvicorn/importer.py
def import_from_string(import_str: str):
    # "main:app" → import main, potem main.app
    
    module_path, attr_name = import_str.split(":")
    # module_path = "main"
    # attr_name = "app"
    
    # Uvicorn importuje main.py
    module = importlib.import_module(module_path)
    # To WYKONUJE cały main.py!
    
    # Uvicorn pobiera obiekt `app`
    app = getattr(module, attr_name)
    # app = main.app
    
    return app
```

**Uvicorn importuje `main.py` i znajduje obiekt `app`.**

---

### Krok 3: Co się dzieje w `main.py` podczas importu?

```python
# main.py (wykonuje się podczas importu przez Uvicorn)

from fastapi import FastAPI

# Tworzy się obiekt FastAPI
app = FastAPI()  # ← To się wykonuje PODCZAS importu

@app.get("/users")
async def get_users():
    return {"users": []}

# Koniec pliku - app jest gotowy
```

**W tym momencie:**
- ✅ `app` został utworzony (obiekt FastAPI)
- ✅ Routing został zarejestrowany
- ❌ **ŻADEN serwer się NIE uruchomił!**
- ❌ **Uvicorn się NIE uruchomił!** (on JUŻ JEST uruchomiony - to ON importuje main.py!)

---

### Krok 4: Uvicorn SPRAWDZA czy `app` jest ASGI callable

```python
# uvicorn/config.py
import inspect

# Uvicorn sprawdza typ aplikacji
def check_app_is_asgi(app):
    # Czy app ma metodę __call__?
    if not callable(app):
        raise TypeError("app must be callable")
    
    # Czy app jest async callable?
    if inspect.iscoroutinefunction(app):
        return True  # ASGI
    
    # Czy app ma __call__ który jest async?
    if hasattr(app, "__call__"):
        if inspect.iscoroutinefunction(app.__call__):
            return True  # ASGI
    
    raise TypeError("app must be ASGI callable")
```

**Uvicorn weryfikuje że `app` spełnia ASGI spec. FastAPI/Starlette mają:**

```python
# starlette/applications.py
class Starlette:
    async def __call__(self, scope, receive, send):
        # ASGI callable
        await self.middleware_stack(scope, receive, send)

# fastapi/applications.py
class FastAPI(Starlette):
    # Dziedziczy __call__ ze Starlette
    pass
```

**`app` to obiekt z metodą `__call__` która jest async - spełnia ASGI!**

---

### Krok 5: Uvicorn CZEKA na requesty (event loop)

```python
# uvicorn/server.py
class Server:
    async def serve(self):
        # Tworzy HTTP server
        server = await self.loop.create_server(
            protocol_factory,
            host=self.config.host,
            port=self.config.port,
        )
        
        # CZEKA na requesty
        await server.serve_forever()
```

**Uvicorn nasłuchuje na porcie 8000. `app` nic nie robi - tylko CZEKA.**

---

### Krok 6: Przychodzi HTTP request

```
Klient → http://127.0.0.1:8000/users
```

```python
# uvicorn/protocols/http/httptools_impl.py
class HttpToolsProtocol:
    def on_message_complete(self):
        # Uvicorn otrzymał pełny HTTP request
        # Tworzy ASGI scope
        scope = {
            'type': 'http',
            'method': 'GET',
            'path': '/users',
            'headers': [...],
            ...
        }
        
        # Uvicorn WYWOŁUJE aplikację (app)
        task = self.loop.create_task(
            self.app(scope, self.receive, self.send)
            #    ↑ to jest Twój `app` (FastAPI)
        )
```

**Uvicorn wywołuje `app` jako funkcję:**

```python
await app(scope, receive, send)
#      ↑ FastAPI.__call__
```

---

### Krok 7: FastAPI ODPOWIADA na wywołanie

```python
# starlette/applications.py
class Starlette:
    async def __call__(self, scope, receive, send):
        # FastAPI otrzymuje scope, receive, send od Uvicorn
        
        # Starlette routing
        route, route_scope = self.router.match(scope)
        
        # FastAPI dependency injection, validation
        response = await route.handle(scope, receive, send)
        
        # FastAPI zwraca response do Uvicorn (przez `send`)
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [...],
        })
        await send({
            'type': 'http.response.body',
            'body': b'{"users": []}',
        })
```

**FastAPI przetwarza request i wysyła response DO UVICORN (przez `send`).**

---

### Krok 8: Uvicorn wysyła HTTP response do klienta

```python
# uvicorn/protocols/http/httptools_impl.py
async def send(message):
    if message['type'] == 'http.response.start':
        # Uvicorn tworzy HTTP response
        self.response_started = True
        status = message['status']
        headers = message['headers']
        
        # Uvicorn formatuje HTTP response
        response = f"HTTP/1.1 {status} OK\r\n"
        for header_name, header_value in headers:
            response += f"{header_name}: {header_value}\r\n"
        response += "\r\n"
        
        # Uvicorn wysyła do klienta
        self.transport.write(response.encode())
    
    elif message['type'] == 'http.response.body':
        # Uvicorn wysyła body
        self.transport.write(message['body'])
```

**Uvicorn wysyła HTTP response do klienta.**

---

## 🎯 Kluczowe zrozumienie:

### FastAPI NIE jest procesem - to tylko obiekt Python!

```python
# main.py
app = FastAPI()  # To tylko obiekt!

# app nie "uruchamia się"
# app nie "nasłuchuje na porcie"
# app nie "tworzy HTTP serwera"
# app nie "wie" że istnieje Uvicorn, Hypercorn, czy cokolwiek

# app to tylko callable:
async def __call__(scope, receive, send):
    # Routing, validation, response
    ...
```

**`app` to pasywny obiekt który CZEKA aż ktoś go wywoła!**

---

### Uvicorn JEST procesem - to aktywny serwer!

```bash
$ uvicorn main:app
```

**Uvicorn:**
1. ✅ Uruchamia się jako główny proces
2. ✅ Importuje `main.py`
3. ✅ Znajduje obiekt `app`
4. ✅ Tworzy HTTP server (nasłuchuje na porcie)
5. ✅ Tworzy event loop
6. ✅ Czeka na requesty
7. ✅ WYWOŁUJE `app(scope, receive, send)` dla każdego requesta
8. ✅ Wysyła HTTP response do klienta

**Uvicorn to aktywny proces który KONTROLUJE wszystko!**

---

## 🔄 Co z Hypercorn?

```bash
hypercorn main:app --reload
```

**DOKŁADNIE TO SAMO!**

1. **Hypercorn uruchamia się** jako główny proces
2. Hypercorn importuje `main.py`
3. Hypercorn znajduje `app`
4. Hypercorn tworzy HTTP server
5. Hypercorn WYWOŁUJE `app(scope, receive, send)`

**FastAPI nie wie czy to Uvicorn czy Hypercorn!**

```python
# main.py
app = FastAPI()

# app jest GŁUCHY I ŚLEPY
# app nie wie kto go wywołuje
# app po prostu odpowiada na wywołanie __call__
```

---

## 📊 Analogia:

### Funkcja Python:

```python
def multiply(x, y):
    return x * y

# Czy funkcja "wie" kto ją wywołuje?
result = multiply(5, 3)  # Ty wywołujesz
result = some_library.call(multiply, 5, 3)  # Biblioteka wywołuje
```

**Funkcja jest pasywna - CZEKA aż ktoś ją wywoła. Nie "wie" kto ją wywołuje!**

### FastAPI (ASGI callable):

```python
app = FastAPI()

# Czy app "wie" kto go wywołuje?
await app(scope, receive, send)  # Uvicorn wywołuje
await app(scope, receive, send)  # Hypercorn wywołuje
await app(scope, receive, send)  # Daphne wywołuje
```

**`app` jest pasywny - CZEKA aż ktoś go wywoła. Nie "wie" kto go wywołuje!**

---

## 💡 Co z `fastapi dev`?

```bash
fastapi dev main.py
```

**To tylko wrapper:**

```python
# fastapi/cli.py
import uvicorn

def dev_command(path: str):
    # fastapi dev po prostu wywołuje Uvicorn!
    uvicorn.run(
        app="main:app",
        reload=True,
    )
```

**Kolejność:**
1. Uruchamiasz `fastapi dev main.py`
2. `fastapi dev` sprawdza czy Uvicorn jest zainstalowany
3. Jeśli tak → wywołuje `uvicorn.run("main:app")`
4. Uvicorn startuje (główny proces)
5. Uvicorn importuje `main.py`
6. Uvicorn wywołuje `app`

**`fastapi dev` to tylko helper do uruchomienia Uvicorn - nic więcej!**

---

## 🔍 Hierarchia (kto kogo kontroluje):

```
┌─────────────────────────────────────────┐
│  Ty (użytkownik)                        │
│  - Uruchamiasz: uvicorn main:app        │
└───────────────┬─────────────────────────┘
                │ uruchamia
                ↓
┌─────────────────────────────────────────┐
│  Uvicorn (główny proces)                │
│  - Tworzy HTTP server                   │
│  - Nasłuchuje na porcie                 │
│  - Importuje main.py                    │
└───────────────┬─────────────────────────┘
                │ importuje
                ↓
┌─────────────────────────────────────────┐
│  main.py (Twój kod)                     │
│  - app = FastAPI()                      │
└───────────────┬─────────────────────────┘
                │ tworzy obiekt
                ↓
┌─────────────────────────────────────────┐
│  app (obiekt FastAPI)                   │
│  - Pasywny callable                     │
│  - CZEKA na wywołanie                   │
└───────────────┬─────────────────────────┘
                │
                ↓ (gdy przychodzi request)
┌─────────────────────────────────────────┐
│  Uvicorn WYWOŁUJE:                      │
│  await app(scope, receive, send)        │
└───────────────┬─────────────────────────┘
                │
                ↓
┌─────────────────────────────────────────┐
│  FastAPI ODPOWIADA:                     │
│  - Routing, validation, response        │
└─────────────────────────────────────────┘
```

**FastAPI NIGDY nie uruchamia Uvicorn - to niemożliwe!**

---

## ❓ Dlaczego FastAPI NIE może "uruchomić Uvicorn"?

### 1. FastAPI to tylko import - wykonuje się PODCZAS importu przez Uvicorn

```python
# main.py
from fastapi import FastAPI

app = FastAPI()  # Wykonuje się gdy Uvicorn robi: import main
```

**W momencie gdy `app` się tworzy, Uvicorn JUŻ JEST uruchomiony!**

---

### 2. FastAPI nie ma kodu który "uruchamia serwer"

```python
# fastapi/applications.py
class FastAPI(Starlette):
    def __init__(self):
        # Tylko inicjalizacja obiektu
        self.routes = []
        self.middleware = []
        # BRAK: server.start(), socket.listen(), etc.
    
    async def __call__(self, scope, receive, send):
        # Tylko obsługa requestu
        # BRAK: uruchamianie serwera
        ...
```

**FastAPI nie ma kodu który uruchamia serwer HTTP - to tylko routing/validation!**

---

### 3. To by było WSGI/ASGI inside-out!

```python
# ❌ To by było absurdalne:
class FastAPI:
    def __init__(self):
        # FastAPI uruchamia Uvicorn?!
        uvicorn.run(self)  # To nie ma sensu!
```

**To by znaczyło że aplikacja uruchamia serwer, a serwer uruchamia aplikację → infinite loop!**

---

## 📝 Podsumowanie:

1. **Uvicorn = główny proces** (uruchamia się jako pierwszy)
2. **FastAPI = pasywny obiekt** (callable który CZEKA na wywołanie)
3. **Uvicorn importuje main.py** → tworzy się `app` (FastAPI)
4. **Uvicorn WYWOŁUJE `app`** dla każdego requesta
5. **FastAPI ODPOWIADA** na wywołanie (routing, validation)
6. **FastAPI NIE WIE** kto go wywołuje (Uvicorn, Hypercorn, Daphne)
7. **FastAPI NIE MOŻE** "uruchomić Uvicorn" - to niemożliwe!
8. **`fastapi dev`** to tylko wrapper który wywołuje `uvicorn.run()`

---

## 🎯 Odpowiedź na Twoje pytanie:

> Skąd FastAPI/Starlette wiedzą, żeby NIE uruchomić domyślnej konfiguracji Uvicorn?

**Odpowiedź:** FastAPI/Starlette **NIGDY** nie uruchamiają Uvicorn! To Uvicorn uruchamia FastAPI!

**FastAPI to tylko callable Python - nie ma możliwości "uruchomić serwer"!**

---

**Zapamiętaj:**

```
❌ BŁĘDNE: FastAPI uruchamia Uvicorn
✅ POPRAWNE: Uvicorn uruchamia FastAPI

❌ BŁĘDNE: FastAPI "wie" że Uvicorn jest uruchomiony
✅ POPRAWNE: FastAPI jest GŁUCHY - nie wie kto go wywołuje

❌ BŁĘDNE: FastAPI "decyduje" nie uruchamiać Uvicorn
✅ POPRAWNE: FastAPI to tylko obiekt - NIE MOŻE uruchomić niczego
```

---
