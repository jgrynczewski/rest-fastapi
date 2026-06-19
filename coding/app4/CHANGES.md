# Zmiany w stosunku do app3

## Secrets Management - Zarządzanie sekretami przez zmienne środowiskowe

**app3:** Sekrety hardcoded w kodzie (SECRET_KEY, DATABASE_URL, etc.)
**app4:** Sekrety w zmiennych środowiskowych + Pydantic Settings

**Różnica:**
- **Hardcoded secrets** = niebezpieczne, ten sam SECRET_KEY dla dev i prod
- **Environment variables** = bezpieczne, różne sekrety dla różnych środowisk

---

## Po co secrets management?

### Problem z hardcoded secrets (app3):
```python
# security.py
SECRET_KEY = "your-secret-key-change-in-production-use-env-variable"
ALGORITHM = "HS256"

# database.py
DATABASE_URL = "postgresql://fastapi_user:fastapi_pass@localhost:5433/fastapi_db"
```

**Zagrożenia:**
1. ❌ SECRET_KEY w kodzie → jeśli wycieknie repo, wycieknie klucz
2. ❌ Ten sam klucz dla dev, staging, prod
3. ❌ Hasło do bazy w kodzie → łatwo wyciec przez commit
4. ❌ Ciężko zmienić sekrety (trzeba modyfikować kod)

### Rozwiązanie - environment variables (app4):
```python
# .env (NIE commitujemy do git!)
SECRET_KEY=super-secret-production-key-32-chars-min
DATABASE_URL=postgresql://prod_user:prod_pass@prod.db.com/prod_db
```

**Zalety:**
1. ✅ Sekrety POZA kodem źródłowym
2. ✅ Różne sekrety dla dev/staging/prod (różne .env)
3. ✅ Łatwa rotacja kluczy (zmiana w .env, restart)
4. ✅ .gitignore → .env nie trafia do repo

---

## Nowe pliki

### .env.example
Template do .env (pokazuje jakie zmienne są potrzebne):
```bash
DATABASE_URL=postgresql://fastapi_user:fastapi_pass@localhost:5433/fastapi_db
SECRET_KEY=your-secret-key-change-in-production-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
DEBUG=true
```

**WAŻNE:**
- `.env.example` commitujemy do git (bez prawdziwych sekretów)
- `.env` NIE commitujemy (prawdziwe sekrety)

### config.py
Pydantic Settings - automatycznie wczytuje zmienne z .env:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

settings = Settings()
```

**Jak działa:**
1. Próbuje wczytać z pliku `.env`
2. Jeśli nie ma .env → czyta ze zmiennych środowiskowych systemowych
3. Jeśli nie ma nigdzie → ValidationError (wymusza ustawienie)

### .gitignore
Zapobiega wyciekowi sekretów:
```
.env           # NIGDY nie commituj!
__pycache__/
*.pyc
venv/
```

---

## Zmodyfikowane pliki

### database.py
**app3:**
```python
DATABASE_URL = "postgresql://fastapi_user:fastapi_pass@localhost:5433/fastapi_db"
engine = create_engine(DATABASE_URL, echo=True)
```

**app4:**
```python
from config import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
```

**Zmiany:**
- ✅ `DATABASE_URL` z settings (nie hardcoded)
- ✅ `echo=settings.DEBUG` (logi tylko w dev)

### security.py
**app3:**
```python
SECRET_KEY = "your-secret-key-change-in-production-use-env-variable"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

**app4:**
```python
from config import settings

def create_access_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

**Zmiany:**
- ✅ `SECRET_KEY` → `settings.SECRET_KEY`
- ✅ `ALGORITHM` → `settings.ALGORITHM`
- ✅ `ACCESS_TOKEN_EXPIRE_MINUTES` → `settings.ACCESS_TOKEN_EXPIRE_MINUTES`

### main.py
- ✅ Title: "Task API with Environment Configuration"
- ✅ Description: wspomnienie o secrets management
- ✅ Root endpoint: info o .env file

---

## Jak używać?

### 1. Development (lokalne środowisko)
```bash
# 1. Skopiuj .env.example → .env
cp .env.example .env

# 2. Edytuj .env (ustaw prawdziwe wartości)
nano .env

# 3. Zainstaluj python-dotenv (jeśli jeszcze nie masz)
pip install pydantic-settings

# 4. Uruchom aplikację
uvicorn main:app --reload

# Settings automatycznie wczyta .env
```

### 2. Production (serwer)
**Opcja A - systemowe environment variables:**
```bash
# Ustaw w systemie (np. w systemd, Docker, Kubernetes)
export SECRET_KEY="super-secret-prod-key-min-32-chars"
export DATABASE_URL="postgresql://prod_user:prod_pass@prod.db/prod_db"
export ENVIRONMENT="production"
export DEBUG="false"

# Uruchom (bez .env)
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Opcja B - .env na serwerze:**
```bash
# 1. Stwórz .env na serwerze (NIGDY nie commituj!)
nano /path/to/app/.env

# 2. Ustaw właściwe uprawnienia (tylko owner może czytać)
chmod 600 .env

# 3. Uruchom
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Docker
```dockerfile
# Dockerfile
FROM python:3.12
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

# NIE kopiuj .env do image!
# Przekaż przez docker run -e lub docker-compose
```

```bash
# Przekaż zmienne przez CLI
docker run -e SECRET_KEY="prod-key" -e DATABASE_URL="..." myapp

# Lub przez docker-compose.yml
version: '3'
services:
  api:
    build: .
    environment:
      - SECRET_KEY=prod-key
      - DATABASE_URL=postgresql://...
```

---

## Best Practices

### ✅ DO:
1. **Nigdy nie commituj .env** (dodaj do .gitignore)
2. **Commituj .env.example** (bez prawdziwych sekretów)
3. **Różne klucze dla dev/prod** (nigdy te same!)
4. **SECRET_KEY min 32 znaki** (entropia!)
5. **Chmod 600 na .env w prod** (tylko owner może czytać)
6. **Rotacja kluczy co X miesięcy** (zmiana SECRET_KEY)

### ❌ DON'T:
1. **NIE commituj .env do git** (.gitignore!)
2. **NIE używaj defaultów w prod** (SECRET_KEY="change-me")
3. **NIE loguj sekretów** (print(settings.SECRET_KEY) ❌)
4. **NIE wysyłaj .env przez email/Slack** (użyj secure vault)
5. **NIE używaj tego samego SECRET_KEY w dev i prod**

---

## Pydantic Settings - szczegóły

### Kolejność wczytywania (priority):
1. **Zmienne środowiskowe systemowe** (najwyższy priorytet)
2. **Plik .env** (jeśli istnieje)
3. **Wartości domyślne** w Settings (np. `ALGORITHM: str = "HS256"`)

**Przykład:**
```bash
# .env
SECRET_KEY=from-dotenv-file

# Terminal
export SECRET_KEY=from-environment

# Pydantic wybierze: "from-environment" (env ma wyższy priorytet)
```

### Walidacja typów:
```python
class Settings(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # musi być int
    DEBUG: bool = False                    # musi być bool
```

```bash
# .env
ACCESS_TOKEN_EXPIRE_MINUTES=abc  # ValidationError: int expected
DEBUG=yes                         # Konwersja: yes/true/1 → True
```

### case_sensitive=False:
```python
model_config = SettingsConfigDict(case_sensitive=False)
```

**Efekt:**
```bash
# .env - wszystkie działają:
SECRET_KEY=xxx
secret_key=xxx
Secret_Key=xxx
```

---

## Deployment scenarios

### Development:
```bash
# .env
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://localhost:5433/dev_db
SECRET_KEY=dev-key-not-secure-ok-for-local
```

### Staging:
```bash
# .env
ENVIRONMENT=staging
DEBUG=false
DATABASE_URL=postgresql://staging.db.com/staging_db
SECRET_KEY=staging-key-32-chars-minimum-secure
```

### Production:
```bash
# .env (lub systemowe env vars)
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://prod.db.com/prod_db
SECRET_KEY=prod-key-32-chars-minimum-super-secure-rotated-monthly
```

**Różne sekrety = izolacja środowisk!**

---

## Troubleshooting

### ValidationError: field required
```python
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
SECRET_KEY
  Field required
```

**Rozwiązanie:**
1. Sprawdź czy masz .env w głównym folderze projektu
2. Sprawdź czy SECRET_KEY jest w .env
3. Sprawdź czy pydantic-settings jest zainstalowane

### .env nie wczytuje się
```python
# Sprawdź ścieżkę
import os
print(os.getcwd())  # .env musi być tutaj!
```

**Rozwiązanie:**
- Przenieś .env do folderu gdzie uruchamiasz `uvicorn main:app`
- Lub ustaw env_file z absolutną ścieżką

---

## Podsumowanie

### app3 (Hardcoded Secrets):
- SECRET_KEY w kodzie ❌
- DATABASE_URL w kodzie ❌
- Ten sam klucz dev/prod ❌
- Sekrety w repo ❌

### app4 (Environment Variables):
- SECRET_KEY w .env/.envs ✅
- DATABASE_URL w .env/.envs ✅
- Różne klucze dev/staging/prod ✅
- .env w .gitignore ✅
- Pydantic Settings z walidacją ✅
- Łatwa rotacja kluczy ✅

**Kluczowa różnica:**
- **app3:** "Sekrety w kodzie → niebezpieczne"
- **app4:** "Sekrety w zmiennych środowiskowych → bezpieczne + flexible"

---

## Dependencies

Dodaj do requirements.txt:
```
pydantic-settings>=2.0.0
python-dotenv>=1.0.0  # opcjonalne (pydantic-settings już to zawiera)
```

**WAŻNE:** Pydantic Settings wymaga Pydantic v2!
