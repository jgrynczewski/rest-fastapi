# Streamlit Frontend dla Task API

Prosty frontend w Pythonie do konsumpcji REST API (bez HTML/CSS/JS).

## Co to jest Streamlit?

**Streamlit** to framework Python do tworzenia webowych aplikacji bez pisania HTML/CSS/JavaScript.
Całość w czystym Pythonie!

### Dlaczego Streamlit?
- ✅ Piszesz tylko Python (zero HTML/CSS/JS)
- ✅ Auto-refresh w przeglądarce przy zmianach kodu
- ✅ Gotowe komponenty UI (przyciski, inputy, tabele)
- ✅ Idealny do prototypów i demo

## Instalacja

```bash
pip install streamlit requests
```

## Uruchomienie

### Krok 0: Konfiguracja (WAŻNE!)

Aplikacja wymaga pliku `.env` z konfiguracją. **Plik `.env` jest już stworzony** i skonfigurowany dla SQLite (nie wymaga PostgreSQL).

Jeśli chcesz użyć PostgreSQL, edytuj plik `.env`:
```bash
# Zakomentuj SQLite i odkomentuj PostgreSQL
DATABASE_URL=postgresql://fastapi_user:fastapi_pass@localhost:5433/fastapi_db
```

### Krok 1: Uruchom FastAPI backend

```bash
# W katalogu app4/
fastapi dev main.py
# lub
# uvicorn main:app --reload
```

Backend będzie dostępny na: http://localhost:8000

**Przy pierwszym uruchomieniu** zostaną automatycznie utworzone tabele w bazie danych (`tasks.db` dla SQLite).

### Krok 2: Uruchom Streamlit frontend

W **nowym terminalu**:

```bash
# W katalogu app4/
streamlit run streamlit_app.py
```

Frontend otworzy się automatycznie w przeglądarce na: http://localhost:8501

## Funkcjonalność

### ✅ Co działa (bez uwierzytelnienia):

1. **Wyświetlanie listy tasków** (GET /v1/tasks)
2. **Dodawanie nowego taska** (POST /v1/tasks)
3. **Edycja taska** (PUT /v1/tasks/{id})
4. **Odświeżanie listy** (przycisk Odśwież)

### ❌ Co NIE działa (wymaga uwierzytelnienia):

- **Usuwanie taska** (DELETE /v1/tasks/{id}) - wymaga roli ADMIN

## Struktura kodu

```python
# Funkcje konsumpcji API
get_all_tasks()      # GET /v1/tasks
create_task(name)    # POST /v1/tasks
update_task(id, name) # PUT /v1/tasks/{id}

# Interfejs użytkownika
main()               # Główna funkcja z UI
```

## Jak to działa?

### Przykład: Dodawanie taska

**Tradycyjny frontend (HTML/JS):**
```html
<input id="name" type="text">
<button onclick="createTask()">Dodaj</button>

<script>
function createTask() {
  fetch('http://localhost:8000/v1/tasks', {
    method: 'POST',
    body: JSON.stringify({name: document.getElementById('name').value})
  });
}
</script>
```

**Streamlit (Python):**
```python
name = st.text_input("Nazwa zadania")
if st.button("Dodaj"):
    requests.post("http://localhost:8000/v1/tasks", json={"name": name})
    st.rerun()
```

## Testowanie

1. Uruchom backend i frontend (kroki powyżej)
2. Otwórz http://localhost:8501
3. Dodaj kilka tasków
4. Edytuj istniejący task
5. Odśwież listę

## Troubleshooting

### Problem: "ValidationError: DATABASE_URL Field required"
Backend wymaga pliku `.env` z konfiguracją. Plik powinien już istnieć w katalogu `app4/.env`.

Jeśli go nie ma, skopiuj `.env.example`:
```bash
cp .env.example .env
```

Lub ręcznie utwórz plik `.env`:
```bash
DATABASE_URL=sqlite:///./tasks.db
SECRET_KEY=super-secret-key-for-development-123456789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
DEBUG=true
```

### Problem: "Connection refused"
- Sprawdź czy backend działa: http://localhost:8000
- Sprawdź czy `API_BASE_URL` w `streamlit_app.py` jest poprawny

### Problem: "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit requests
```

### Problem: Frontend nie widzi zmian w API
- Kliknij przycisk "🔄 Odśwież" w aplikacji
- Lub naciśnij `R` w Streamlit (reload)

## Dodatkowe zasoby

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Gallery](https://streamlit.io/gallery) - przykłady aplikacji
- [API Documentation](http://localhost:8000/docs) - Swagger UI

---

**Dla kursantów:** To jest minimalistyczny przykład konsumpcji REST API.
W prawdziwej aplikacji produkcyjnej używalibyście frameworków jak React, Vue, Angular.
Streamlit jest świetny do prototypów i data apps!