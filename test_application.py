"""
Тестовый скрипт для проверки всех модулей приложения
"""

import sys
import os

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_database():
    """Тестирование модуля базы данных"""
    print("\n" + "=" * 60)
    print("ТЕСТ 1: Модуль базы данных")
    print("=" * 60)

    from database.db_manager import DatabaseManager

    try:
        db = DatabaseManager("database/test_drone.db")
        print("✓ База данных создана успешно")

        # Проверка таблиц
        frames = db.get_components("frames")
        print(f"✓ Загружено корпусов: {len(frames)}")

        motors = db.get_components("motors")
        print(f"✓ Загружено двигателей: {len(motors)}")

        batteries = db.get_components("batteries")
        print(f"✓ Загружено аккумуляторов: {len(batteries)}")

        # Добавление компонента
        new_frame = {
            'name': 'Test Frame',
            'mass': 150.0,
            'description': 'Тестовый корпус'
        }
        frame_id = db.add_component('frames', new_frame)
        print(f"✓ Добавлен тестовый компонент с ID: {frame_id}")

        # Удаление тестового компонента
        db.delete_component('frames', frame_id)
        print("✓ Тестовый компонент удален")

        # Очистка
        os.remove("database/test_drone.db")
        print("✓ Тестовая база данных удалена")

        print("\n Модуль базы данных работает корректно!")
        return True

    except Exception as e:
        print(f"\n Ошибка в модуле базы данных: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_calculator():
    """Тестирование модуля калькулятора"""
    print("\n" + "=" * 60)
    print("ТЕСТ 2: Модуль калькулятора")
    print("=" * 60)

    from modules.calculator import DroneCalculator

    try:
        calc = DroneCalculator()
        print("✓ Калькулятор инициализирован")

        # Тест валидации массы
        valid, msg = calc.validate_mass(100.0)
        assert valid, "Валидация массы не прошла"
        print("✓ Валидация массы работает")

        # Тест валидации количества
        valid, msg = calc.validate_quantity(4)
        assert valid, "Валидация количества не прошла"
        print("✓ Валидация количества работает")

        # Тест расчета массы компонента
        mass = calc.calculate_component_mass(50.0, 4)
        assert mass == 200.0, f"Ожидалось 200.0, получено {mass}"
        print("✓ Расчет массы компонента работает")

        # Тест расчета общей массы
        components = {
            'frame': {'name': 'Test Frame', 'mass': 100.0, 'qty': 1},
            'motor': {'name': 'Test Motor', 'mass': 50.0, 'qty': 4}
        }
        results = calc.calculate_total_mass(components)
        assert results['total_mass'] == 300.0, f"Ожидалось 300.0, получено {results['total_mass']}"
        print(f"✓ Расчет общей массы работает: {results['total_mass']}г")

        # Тест определения категории
        category = calc.get_weight_category(300.0)
        print(f"✓ Определение категории работает: {category}")

        # Тест форматирования массы
        formatted = calc.format_mass(1500.0)
        print(f"✓ Форматирование массы работает: {formatted}")

        print("\n Модуль калькулятора работает корректно!")
        return True

    except Exception as e:
        print(f"\n Ошибка в модуле калькулятора: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualizer():
    """Тестирование модуля визуализации"""
    print("\n" + "=" * 60)
    print("ТЕСТ 3: Модуль визуализации")
    print("=" * 60)

    from modules.visualizer import DroneVisualizer
    import matplotlib.pyplot as plt

    try:
        viz = DroneVisualizer()
        print("✓ Визуализатор инициализирован")

        # Тест создания круговой диаграммы
        test_data = {
            'Корпус': 100.0,
            'Двигатели': 200.0,
            'Аккумулятор': 300.0
        }

        fig = viz.create_pie_chart(test_data, "Тестовая диаграмма")
        assert fig is not None, "Диаграмма не создана"
        print("✓ Круговая диаграмма создана")

        # Очистка
        plt.close(fig)
        print("✓ Диаграмма закрыта")

        print("\n Модуль визуализации работает корректно!")
        return True

    except Exception as e:
        print(f"\n Ошибка в модуле визуализации: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_report_generator():
    """Тестирование модуля генерации отчетов"""
    print("\n" + "=" * 60)
    print("ТЕСТ 4: Модуль генерации отчетов")
    print("=" * 60)

    from modules.report import ReportGenerator

    try:
        report_gen = ReportGenerator()
        print("✓ Генератор отчетов инициализирован")

        # Тестовые данные расчета
        test_results = {
            'components': {
                'frame': {
                    'name': 'Test Frame',
                    'unit_mass': 100.0,
                    'quantity': 1,
                    'total_mass': 100.0
                },
                'motor': {
                    'name': 'Test Motor',
                    'unit_mass': 50.0,
                    'quantity': 4,
                    'total_mass': 200.0
                }
            },
            'total_mass': 300.0,
            'component_count': 2
        }

        # Тест генерации отчета
        report = report_gen.generate_text_report(test_results)
        assert len(report) > 0, "Отчет пустой"
        assert "ОТЧЕТ О МАССЕ" in report, "Заголовок отчета не найден"
        assert "300.0" in report, "Общая масса не найдена в отчете"
        print("✓ Текстовый отчет сгенерирован")
        print(f"✓ Длина отчета: {len(report)} символов")

        # Тест сохранения отчета
        filename = report_gen.save_report_to_file(report, "test_report.txt")
        assert os.path.exists(filename), "Файл отчета не сохранен"
        print(f"✓ Отчет сохранен в файл: {filename}")

        # Очистка
        os.remove(filename)
        print("✓ Тестовый файл удален")

        print("\n Модуль генерации отчетов работает корректно!")
        return True

    except Exception as e:
        print(f"\n Ошибка в модуле генерации отчетов: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Главная функция тестирования"""
    print("\n" + "=" * 60)
    print("ЗАПУСК ТЕСТОВ ПРИЛОЖЕНИЯ 'КАЛЬКУЛЯТОР МАССЫ ДРОНА'")
    print("=" * 60)

    results = []

    # Запуск всех тестов
    results.append(("База данных", test_database()))
    results.append(("Калькулятор", test_calculator()))
    results.append(("Визуализация", test_visualizer()))
    results.append(("Генерация отчетов", test_report_generator()))

    # Итоговые результаты
    print("\n" + "=" * 60)
    print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for module_name, result in results:
        status = " ПРОЙДЕН" if result else " ПРОВАЛЕН"
        print(f"{module_name}: {status}")

    print("\n" + "=" * 60)
    print(f"Пройдено тестов: {passed}/{total}")

    if passed == total:
        print(" ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 60)
        return True
    else:
        print("⚠ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)