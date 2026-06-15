from fastapi import FastAPI

# Inicjalizacja aplikacji FastAPI
app = FastAPI(
    title="Weather API",  # Zmień na "Stats API" dla ścieżki B
    description="Simple weather forecast API",
    version="1.0.0"
)

# TODO 1: Zaimplementuj root endpoint
# Endpoint: GET /
# Powinien zwrócić: {"message": "Welcome to Weather API", "version": "1.0.0"}
#
# Wskazówka: Użyj dekoratora @app.get("/") i zwróć dict
@app.get("/")
def root():
    """
    Root endpoint - zwraca podstawowe informacje o API
    """
    pass  # Zamień pass na właściwą implementację


# TODO 2: Zaimplementuj endpoint z path parameter
# Endpoint: GET /weather/{city}
# Parametr: city (string) - nazwa miasta
# Dla GET /weather/warsaw
# Powinien zwrócić: {"city": "warsaw", "temperature": 22, "condition": "Sunny"}
#
# Wskazówka:
# - Użyj @app.get("/weather/{city}")
# - Dodaj parametr city: str do funkcji
# - Zwróć dict z kluczami: city, temperature, condition


# TODO 3: Zaimplementuj endpoint z query parameters
# Endpoint: GET /weather
# Query params:
#   - city (string, wymagany)
#   - days (int, opcjonalny, default=1)
#
# Przykład wywołania: GET /weather?city=Warsaw&days=3
# Powinien zwrócić: {
#     "city": "Warsaw",
#     "days": 3,
#     "forecast": ["Sunny", "Cloudy", "Rainy"]
# }
#
# Wskazówka:
# - Query parametry to zwykłe argumenty funkcji (bez {})
# - Opcjonalny parametr: days: int = 1
# - Forecast możesz zrobić jako listę ["Sunny", "Cloudy", "Rainy"] * days


# TODO 4: Zaimplementuj endpoint z wieloma path parameters
# Endpoint: GET /forecast/{city}/{days}
# Parametry:
#   - city (string)
#   - days (int)
#
# Przykład wywołania: GET /forecast/Warsaw/7
# Powinien zwrócić: {
#     "city": "Warsaw",
#     "days": 7,
#     "forecast": ["Sunny", "Cloudy", "Rainy", "Sunny", "Cloudy", "Rainy", "Sunny"]
# }
#
# Wskazówka:
# - Możesz mieć wiele {parametrów} w path
# - Wszystkie muszą być też argumentami funkcji


# Uruchomienie serwera:
# uvicorn 01:app --reload
#
# Dokumentacja Swagger:
# http://localhost:8000/docs
