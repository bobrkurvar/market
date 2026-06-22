import asyncio
import sys

from scripts.create_admins import main as create_admins_main
from scripts.seed_data import main as seed_data_main

async def interactive_menu():
    while True:
        print("\n=== Менеджер скриптов myMarket ===")
        print("1. Создать администратора (create_admins.py)")
        print("2. Сгенерировать тестовые данные (seed_data.py)")
        print("0. Выход")
        print("==================================\n")

        choice = input("Выберите скрипт для запуска (1, 2 или 0): ").strip()

        if choice == "1":
            print("\n⏳ Запуск create_admins...")
            await create_admins_main()
            print("✅ Готово!")
        elif choice == "2":
            print("\n⏳ Запуск seed_data (это может занять время)...")
            await seed_data_main()
            print("✅ Готово!")
        elif choice == "0":
            print("Выход.")
            sys.exit(0)
        else:
            print("❌ Неверный выбор. Попробуйте снова.")
            await interactive_menu()

def main():
    try:
        asyncio.run(interactive_menu())
    except KeyboardInterrupt:
        print("\nВыход из программы.")
        sys.exit(0)

if __name__ == "__main__":
    main()