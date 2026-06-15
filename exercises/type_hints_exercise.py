"""
Ćwiczenie: Dodaj type hints na podstawie opisów

ZADANIE:
- Dodaj type hints do wszystkich funkcji i zmiennych poniżej
- Użyj nowoczesnej składni Python 3.10+ (int | str zamiast Union[int, str])
- Sprawdź poprawność: mypy type_hints_exercise.py --strict

UWAGA: Nie zmieniaj logiki kodu, tylko dodaj type hints!

CO ROBI mypy --strict?
Flaga --strict włącza wszystkie restrykcyjne opcje mypy:
- disallow_untyped_defs - KAŻDA funkcja MUSI mieć type hints (parametry + return)
- disallow_any_unimported - nie pozwala na Any z niezaimportowanych modułów
- warn_return_any - ostrzega gdy funkcja zwraca Any
- warn_unused_ignores - ostrzega o niepotrzebnych # type: ignore
- no_implicit_optional - None w default NIE oznacza automatycznie Optional
- strict_equality - sprawdza czy porównujesz zgodne typy
...i wiele innych

Bez --strict mypy jest bardziej wyrozumiały (pozwala na brak typów w niektórych miejscach).
Z --strict = pełna dyscyplina typów!
"""

# 1. Funkcja calculate_total przyjmuje listę cen (liczby zmiennoprzecinkowe)
#    i zwraca sumę jako liczbę zmiennoprzecinkową
def calculate_total(prices):
    return sum(prices)


# 2. Zmienna user_id może być liczbą całkowitą LUB tekstem
user_id = 123  # lub "abc"


# 3. Funkcja get_user_name przyjmuje user_id (może być int lub str)
#    i zwraca imię jako tekst LUB None jeśli nie znaleziono
def get_user_name(uid):
    users = {123: "Jan", "abc": "Anna"}
    return users.get(uid)


# 4. Zmienna config przechowuje słownik gdzie klucze to tekst,
#    wartości to liczby całkowite
config = {"timeout": 30, "retries": 3, "max_connections": 100}


# 5. Funkcja process_items przyjmuje dowolną ilość liczb całkowitych
#    jako argumenty i nic nie zwraca (wypisuje tylko na ekran)
def process_items(*item_ids):
    for item_id in item_ids:
        print(f"Processing item {item_id}")


# 6. Zmienna status może przyjąć tylko jedną z trzech wartości:
#    "pending", "active", "inactive"
status = "pending"


# 7. Funkcja apply_discount przyjmuje cenę (float), opcjonalny procent
#    zniżki (float, domyślnie None) i zwraca nową cenę (float)
def apply_discount(price, discount=None):
    if discount:
        return price * (1 - discount / 100)
    return price


# 8. Zmienna items to lista słowników, gdzie każdy słownik ma klucze
#    "id" (int) i "name" (str)
items = [
    {"id": 1, "name": "Apple"},
    {"id": 2, "name": "Banana"},
    {"id": 3, "name": "Orange"}
]


# 9. Funkcja callback_handler przyjmuje funkcję (która bierze int
#    i zwraca str) oraz liczbę całkowitą, i zwraca tekst
def callback_handler(callback, value):
    return callback(value)


# 10. Zmienna metadata może być dowolnego typu (wyłącz sprawdzanie typów)
metadata = {"anything": "goes", "here": 123, "even": [1, 2, 3]}


# Test code (nie zmieniaj)
if __name__ == "__main__":
    print(calculate_total([10.5, 20.3, 5.2]))
    print(get_user_name(123))
    print(get_user_name("abc"))
    print(get_user_name(999))
    process_items(1, 2, 3, 4, 5)
    print(apply_discount(100.0, 10.0))
    print(apply_discount(100.0))
    print(callback_handler(str, 42))