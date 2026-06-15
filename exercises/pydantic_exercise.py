"""
Ćwiczenie: Pydantic - Survey Response Validator

ZADANIE:
Zaimplementuj model SurveyResponse do walidacji odpowiedzi z ankiety.
Użyj BaseModel, Field, type hints i walidacji.

UWAGA: Uruchom ten plik aby sprawdzić czy działa!
"""

from pydantic import BaseModel, Field, ValidationError


class SurveyResponse(BaseModel):
    # respondent_id: string w formacie "R-12345" (R- + dokładnie 5 cyfr)
    # Użyj Field z pattern (regex: ^R-\d{5}$)
    respondent_id: ...  # TODO

    # age: liczba całkowita, zakres 18-100
    # Użyj Field z odpowiednimi constraints (ge, le)
    age: ...  # TODO

    # satisfaction_score: liczba całkowita, zakres 1-5
    # Użyj Field z odpowiednimi constraints
    satisfaction_score: ...  # TODO

    # category: tylko jedna z wartości: "product", "service", "support"
    # Użyj Literal (zaimportuj z typing)
    category: ...  # TODO

    # email: string, podstawowa walidacja email (pattern: .+@.+\..+)
    # Użyj Field z pattern
    email: ...  # TODO

    # comment: opcjonalny string (może być None), ale jeśli podany to min 10 znaków
    # Użyj Field z min_length i odpowiedniego typu (str | None)
    comment: ...  # TODO


# ============================================================================
# TESTY - uruchom ten plik aby sprawdzić czy działa!
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("TEST 1: Poprawne dane - bezpośrednio")
    print("=" * 70)

    response1 = SurveyResponse(
        respondent_id="R-12345",
        age=25,
        satisfaction_score=4,
        category="product",
        email="user@example.com",
        comment="Great product, very satisfied with the quality!"
    )
    print(f"✅ {response1}\n")


    print("=" * 70)
    print("TEST 2: Poprawne dane - z dict użwając **")
    print("=" * 70)

    data = {
        "respondent_id": "R-99999",
        "age": 45,
        "satisfaction_score": 5,
        "category": "service",
        "email": "anna@company.pl",
        "comment": None  # Opcjonalne - może być None
    }
    response2 = SurveyResponse(**data)
    print(f"✅ {response2}\n")


    print("=" * 70)
    print("TEST 3: Export do JSON")
    print("=" * 70)

    json_output = response1.model_dump_json(indent=2)
    print(json_output)
    print()


    print("=" * 70)
    print("TEST 4: Błędne dane - walidacja")
    print("=" * 70)

    # Test 4a: Zły wiek (poniżej 18)
    print("\n[Test 4a] age=15 (za młody):")
    try:
        bad1 = SurveyResponse(
            respondent_id="R-11111",
            age=15,  # ❌ Za młody
            satisfaction_score=3,
            category="product",
            email="test@example.com"
        )
    except ValidationError as e:
        print(f"❌ ValidationError: {e.errors()[0]['msg']}")

    # Test 4b: Zły score (poza zakresem)
    print("\n[Test 4b] satisfaction_score=6 (poza zakresem 1-5):")
    try:
        bad2 = SurveyResponse(
            respondent_id="R-22222",
            age=30,
            satisfaction_score=6,  # ❌ Poza zakresem
            category="service",
            email="test@example.com"
        )
    except ValidationError as e:
        print(f"❌ ValidationError: {e.errors()[0]['msg']}")

    # Test 4c: Zły format respondent_id
    print("\n[Test 4c] respondent_id='R-123' (zły format, powinno być R-XXXXX):")
    try:
        bad3 = SurveyResponse(
            respondent_id="R-123",  # ❌ Tylko 3 cyfry zamiast 5
            age=30,
            satisfaction_score=4,
            category="support",
            email="test@example.com"
        )
    except ValidationError as e:
        print(f"❌ ValidationError: {e.errors()[0]['msg']}")

    # Test 4d: Zły email
    print("\n[Test 4d] email='invalid' (zły format):")
    try:
        bad4 = SurveyResponse(
            respondent_id="R-33333",
            age=30,
            satisfaction_score=4,
            category="product",
            email="invalid"  # ❌ Brak @
        )
    except ValidationError as e:
        print(f"❌ ValidationError: {e.errors()[0]['msg']}")

    # Test 4e: Comment za krótki
    print("\n[Test 4e] comment='Too short' (mniej niż 10 znaków):")
    try:
        bad5 = SurveyResponse(
            respondent_id="R-44444",
            age=30,
            satisfaction_score=4,
            category="product",
            email="test@example.com",
            comment="Short"  # ❌ Tylko 5 znaków
        )
    except ValidationError as e:
        print(f"❌ ValidationError: {e.errors()[0]['msg']}")

    # Test 4f: Zła kategoria
    print("\n[Test 4f] category='invalid' (nie ma takiej opcji):")
    try:
        bad6 = SurveyResponse(
            respondent_id="R-55555",
            age=30,
            satisfaction_score=4,
            category="invalid",  # ❌ Nie ma takiej kategorii
            email="test@example.com"
        )
    except ValidationError as e:
        print(f"❌ ValidationError: {e.errors()[0]['msg']}")

    print("\n" + "=" * 70)
    print("✅ Wszystkie testy zakończone!")
    print("=" * 70)