import secrets
import string
import json
from datetime import datetime, timedelta


class CodeManager:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CodeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.current_code = None
        self.generated_at = None
        self.history = []

        self._initialized = True

    def generate(self, length):
        """
        Generuje kod o długości:
        4 lub 6  -> PIN: cyfry 0-9
        12 lub 16 -> token: 0-9, a-z, A-Z
        """

        if length not in (4, 6, 12, 16):
            raise ValueError(
                "Długość musi wynosić 4, 6, 12 albo 16."
            )

        # Blokada zmiany kodu przez godzinę
        if self.current_code is not None and self.generated_at is not None:
            elapsed = datetime.now() - self.generated_at

            if elapsed < timedelta(hours=1):
                remaining = timedelta(hours=1) - elapsed
                minutes = int(remaining.total_seconds() // 60)

                raise RuntimeError(
                    f"Nie można zmienić kodu przez godzinę. "
                    f"Pozostało około {minutes} minut."
                )

        # PIN
        if length in (4, 6):
            alphabet = string.digits

        # Token
        else:
            alphabet = string.digits + string.ascii_lowercase + string.ascii_uppercase

        # secrets jest przeznaczone do generowania wartości kryptograficznie bezpiecznych
        code = ''.join(secrets.choice(alphabet) for _ in range(length))

        # Niepowtarzalna historia
        if code not in self.history:
            self.history.insert(0, code)

        # Maksymalnie 3 ostatnie unikalne kody
        self.history = self.history[:3]

        self.current_code = code
        self.generated_at = datetime.now()

        return code

    def display(self):
        """Wyświetlenie aktualnego kodu."""
        if self.current_code is None:
            print("Brak wygenerowanego kodu.")
        else:
            print(f"Aktualny kod: {self.current_code}")

    def save_to_file(self, filename="code.txt"):
        """Zapis aktualnego kodu do pliku."""
        if self.current_code is None:
            raise RuntimeError("Brak kodu do zapisania.")

        with open(filename, "w", encoding="utf-8") as file:
            file.write(self.current_code)

        print(f"Kod zapisano do pliku: {filename}")

    def serialize(self, filename="data.json"):
        """Serializacja danych do JSON."""
        data = {
            "current_code": self.current_code,
            "generated_at": (
                self.generated_at.isoformat()
                if self.generated_at else None
            ),
            "history": self.history
        }

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print(f"Dane zapisano do: {filename}")

    def deserialize(self, filename="data.json"):
        """Odczyt danych z pliku JSON."""
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.current_code = data.get("current_code")
        self.history = data.get("history", [])

        generated_at = data.get("generated_at")

        if generated_at:
            self.generated_at = datetime.fromisoformat(generated_at)
        else:
            self.generated_at = None


def main():
    manager = CodeManager()

    print("=== GENERATOR PIN / TOKEN ===")
    print("Dostępne długości: 4, 6, 12, 16")

    try:
        length = int(input("Podaj długość kodu: "))

        code = manager.generate(length)

        print("\nWygenerowany kod:")
        manager.display()

        answer = input("\nCzy zapisać kod do pliku? (t/n): ")

        if answer.lower() == "t":
            filename = input("Podaj nazwę pliku: ")
            manager.save_to_file(filename)

        # Serializacja danych
        manager.serialize("code_data.json")

        print("\nHistoria ostatnich 3 kodów:")
        for item in manager.history:
            print(item)

    except ValueError as e:
        print(f"Błąd: {e}")

    except RuntimeError as e:
        print(f"Błąd: {e}")


if __name__ == "__main__":
    main()
