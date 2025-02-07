import os
import sys

LICENSE_FILE = "LICENSE"

def check_license():
    if not os.path.exists(LICENSE_FILE):
        print("\n❌ ОШИБКА: Файл лицензии отсутствует ❌")
        print("Этот код закрыт для использования. Без лицензии его использование запрещено.")
        sys.exit(1)  # Останавливает сервер, если файла нет

    with open(LICENSE_FILE, "r", encoding="utf-8") as f:
        license_text = f.read()

    print("\n" + "=" * 60)
    print(license_text)
    print("=" * 60 + "\n")

    input("Нажмите Enter, если вы согласны с условиями и хотите продолжить... ")

