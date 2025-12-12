"""
Главный файл приложения "Калькулятор массы дрона"

Приложение предназначено для расчета общей массы беспилотного летательного аппарата (БПЛА)
на основе выбранных компонентов. Включает базу данных компонентов, визуализацию данных
и генерацию отчетов.

Дата: 2025
"""

import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.gui import DroneCalculatorGUI

def main():
    """Главная функция приложения"""
    print("=" * 60)
    print("Запуск приложения: Калькулятор массы дрона")
    print("=" * 60)
    print("\nИнициализация компонентов...")

    try:
        # Создаем и запускаем GUI
        app = DroneCalculatorGUI()
        print("✓ GUI инициализирован")
        print("✓ База данных подключена")
        print("✓ Компоненты загружены")
        print("\nПриложение готово к работе!")
        print("-" * 60)

        app.run()

    except Exception as e:
        print(f"\n✗ Ошибка при запуске приложения: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
