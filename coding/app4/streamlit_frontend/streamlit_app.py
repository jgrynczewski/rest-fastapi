"""
Prosty frontend Streamlit do konsumpcji Task API.

Uruchomienie:
1. Upewnij się że FastAPI działa: uvicorn main:app --reload
2. Uruchom Streamlit: streamlit run streamlit_app.py
3. Otwórz przeglądarkę: http://localhost:8501

Funkcjonalność:
- Wyświetlanie listy wszystkich tasków
- Dodawanie nowego taska
- Edycja istniejącego taska
- Odświeżanie listy
"""

import streamlit as st
import requests
from typing import List, Dict

# Konfiguracja API
API_BASE_URL = "http://localhost:8000/v1"


# ============================================================================
# FUNKCJE POMOCNICZE - konsumpcja REST API
# ============================================================================

def get_all_tasks() -> List[Dict]:
    """Pobiera wszystkie taski z API (GET /v1/tasks)."""
    try:
        response = requests.get(f"{API_BASE_URL}/tasks")
        response.raise_for_status()
        data = response.json()
        return data.get("tasks", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Błąd pobierania tasków: {e}")
        return []


def create_task(name: str) -> bool:
    """Tworzy nowy task (POST /v1/tasks)."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/tasks",
            json={"name": name}
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Błąd tworzenia taska: {e}")
        return False


def update_task(task_id: int, name: str) -> bool:
    """Aktualizuje istniejący task (PUT /v1/tasks/{id})."""
    try:
        response = requests.put(
            f"{API_BASE_URL}/tasks/{task_id}",
            json={"name": name}
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Błąd aktualizacji taska: {e}")
        return False


# ============================================================================
# INTERFEJS UŻYTKOWNIKA
# ============================================================================

def main():
    # Nagłówek aplikacji
    st.title("📋 Task Manager")
    st.markdown("Prosty frontend do konsumpcji REST API (FastAPI)")

    # Separator
    st.divider()

    # ========================================================================
    # SEKCJA 1: Dodawanie nowego taska
    # ========================================================================
    st.subheader("➕ Dodaj nowy task")

    with st.form("create_task_form"):
        new_task_name = st.text_input(
            "Nazwa zadania",
            placeholder="Wpisz nazwę zadania (min 3 znaki)...",
            max_chars=100
        )

        submit_create = st.form_submit_button("Dodaj task", use_container_width=True)

        if submit_create:
            if len(new_task_name) < 3:
                st.error("Nazwa musi mieć minimum 3 znaki!")
            else:
                if create_task(new_task_name):
                    st.success(f"✅ Task '{new_task_name}' został dodany!")
                    st.rerun()  # Odśwież stronę żeby pokazać nowy task

    # Separator
    st.divider()

    # ========================================================================
    # SEKCJA 2: Lista wszystkich tasków
    # ========================================================================
    st.subheader("📝 Lista tasków")

    # Przycisk odświeżania
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Odśwież", use_container_width=True):
            st.rerun()

    # Pobierz taski z API
    tasks = get_all_tasks()

    if not tasks:
        st.info("Brak tasków. Dodaj pierwszy!")
    else:
        st.write(f"**Liczba tasków:** {len(tasks)}")

        # Wyświetl każdy task
        for task in tasks:
            task_id = task["id"]
            task_name = task["name"]

            # Każdy task w osobnym kontenerze
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])

                # Kolumna 1: ID i nazwa
                with col1:
                    st.markdown(f"**#{task_id}** — {task_name}")

                # Kolumna 2: Przycisk edycji
                with col2:
                    if st.button("✏️ Edytuj", key=f"edit_{task_id}", use_container_width=True):
                        st.session_state[f"editing_{task_id}"] = True
                        st.rerun()

                # Jeśli task jest w trybie edycji
                if st.session_state.get(f"editing_{task_id}", False):
                    with st.form(f"edit_form_{task_id}"):
                        updated_name = st.text_input(
                            "Nowa nazwa",
                            value=task_name,
                            max_chars=100
                        )

                        col_save, col_cancel = st.columns(2)

                        with col_save:
                            submit_update = st.form_submit_button("💾 Zapisz", use_container_width=True)

                        with col_cancel:
                            submit_cancel = st.form_submit_button("❌ Anuluj", use_container_width=True)

                        if submit_update:
                            if len(updated_name) < 1:
                                st.error("Nazwa nie może być pusta!")
                            else:
                                if update_task(task_id, updated_name):
                                    st.success(f"✅ Task #{task_id} zaktualizowany!")
                                    st.session_state[f"editing_{task_id}"] = False
                                    st.rerun()

                        if submit_cancel:
                            st.session_state[f"editing_{task_id}"] = False
                            st.rerun()

    # ========================================================================
    # INFORMACJA O DELETE (wymaga auth)
    # ========================================================================
    st.divider()
    st.info("""
    ℹ️ **Uwaga:** Usuwanie tasków (DELETE) wymaga uwierzytelnienia z rolą ADMIN
    i nie jest dostępne w tym prostym frontendzie.
    """)


# ============================================================================
# URUCHOMIENIE APLIKACJI
# ============================================================================
if __name__ == "__main__":
    main()