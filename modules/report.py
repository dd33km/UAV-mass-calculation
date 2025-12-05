"""
Модуль генерации отчетов.
Создает текстовые отчеты о конфигурации и массе дрона.
"""

from datetime import datetime
from typing import Dict


class ReportGenerator:
    """Класс для генерации отчетов о дроне"""

    def __init__(self):
        """Инициализация генератора отчетов"""
        pass

    def generate_text_report(self, calculation_results: Dict, calc_id: int = None) -> str:
        """
        Генерирует текстовый отчет о конфигурации дрона

        Args:
            calculation_results: Результаты расчета из DroneCalculator
            calc_id: ID расчета в базе данных

        Returns:
            Текстовый отчет
        """
        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("ОТЧЕТ О МАССЕ БЕСПИЛОТНОГО ЛЕТАТЕЛЬНОГО АППАРАТА (БПЛА)")
        report_lines.append("=" * 70)
        report_lines.append("")

        # Информация о расчете
        report_lines.append(f"Дата и время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        if calc_id:
            report_lines.append(f"ID конфигурации: {calc_id}")
        report_lines.append("")

        # Детальная информация о компонентах
        report_lines.append("-" * 70)
        report_lines.append("СОСТАВ КОНФИГУРАЦИИ:")
        report_lines.append("-" * 70)
        report_lines.append("")

        components = calculation_results.get('components', {})

        # Названия компонентов на русском
        component_names_ru = {
            'frame': 'Корпус',
            'motor': 'Двигатели',
            'battery': 'Аккумулятор',
            'flight_controller': 'Контроллер полета',
            'propeller': 'Пропеллеры',
            'camera': 'Камера/Полезная нагрузка'
        }

        for comp_type, comp_data in components.items():
            comp_name_ru = component_names_ru.get(comp_type, comp_type)
            report_lines.append(f"{comp_name_ru}:")
            report_lines.append(f"  Модель: {comp_data['name']}")
            report_lines.append(f"  Масса единицы: {comp_data['unit_mass']:.1f} г")
            report_lines.append(f"  Количество: {comp_data['quantity']} шт.")
            report_lines.append(f"  Общая масса: {comp_data['total_mass']:.1f} г")
            report_lines.append("")

        # Итоговая информация
        report_lines.append("-" * 70)
        report_lines.append("ИТОГОВЫЕ ДАННЫЕ:")
        report_lines.append("-" * 70)
        report_lines.append("")

        total_mass = calculation_results.get('total_mass', 0)
        component_count = calculation_results.get('component_count', 0)

        report_lines.append(f"Количество типов компонентов: {component_count}")
        report_lines.append(f"Общая масса БПЛА: {total_mass:.1f} г ({total_mass / 1000:.3f} кг)")
        report_lines.append("")

        # Категория дрона
        category = self._get_weight_category(total_mass)
        report_lines.append(f"Категория БПЛА: {category}")
        report_lines.append("")

        # Процентное распределение
        report_lines.append("-" * 70)
        report_lines.append("ПРОЦЕНТНОЕ РАСПРЕДЕЛЕНИЕ МАССЫ:")
        report_lines.append("-" * 70)
        report_lines.append("")

        for comp_type, comp_data in components.items():
            comp_name_ru = component_names_ru.get(comp_type, comp_type)
            percentage = (comp_data['total_mass'] / total_mass * 100) if total_mass > 0 else 0
            report_lines.append(f"{comp_name_ru}: {percentage:.1f}%")

        report_lines.append("")

        # Рекомендации
        report_lines.append("-" * 70)
        report_lines.append("РЕКОМЕНДАЦИИ:")
        report_lines.append("-" * 70)
        report_lines.append("")

        recommendations = self._generate_recommendations(total_mass, components)
        for rec in recommendations:
            report_lines.append(f"• {rec}")

        report_lines.append("")
        report_lines.append("=" * 70)
        report_lines.append("КОНЕЦ ОТЧЕТА")
        report_lines.append("=" * 70)

        return "\n".join(report_lines)

    def _get_weight_category(self, total_mass: float) -> str:
        """Определяет категорию дрона по массе"""
        if total_mass < 250:
            return "Микро (< 250г) - не требует регистрации"
        elif total_mass < 500:
            return "Мини (250-500г)"
        elif total_mass < 2000:
            return "Средний (0.5-2 кг)"
        elif total_mass < 25000:
            return "Большой (2-25 кг)"
        else:
            return "Тяжелый (> 25 кг) - требуется специальное разрешение"

    def _generate_recommendations(self, total_mass: float, components: Dict) -> list:
        """Генерирует рекомендации на основе конфигурации"""
        recommendations = []

        # Рекомендации по массе
        if total_mass < 250:
            recommendations.append("Дрон не требует регистрации в большинстве стран")
            recommendations.append("Подходит для использования в помещениях и городских условиях")
        elif total_mass < 500:
            recommendations.append("Легкий дрон, хорошая маневренность")
            recommendations.append("Рекомендуется для любительской съемки и FPV полетов")
        elif total_mass < 2000:
            recommendations.append("Средний дрон, баланс между грузоподъемностью и маневренностью")
            recommendations.append("Подходит для профессиональной фото/видеосъемки")
        else:
            recommendations.append("Тяжелый дрон, высокая грузоподъемность")
            recommendations.append("Требуется регистрация и получение разрешений")
            recommendations.append("Рекомендуется для промышленного применения")

        # Проверка баланса компонентов
        if 'battery' in components:
            battery_percentage = (components['battery']['total_mass'] / total_mass * 100) if total_mass > 0 else 0
            if battery_percentage < 20:
                recommendations.append("Низкая доля аккумулятора - возможно короткое время полета")
            elif battery_percentage > 40:
                recommendations.append("Высокая доля аккумулятора - хорошее время полета, но снижена маневренность")

        if 'motor' in components and 'frame' in components:
            motor_count = components['motor']['quantity']
            if motor_count == 4:
                recommendations.append("Квадрокоптер - оптимальная конфигурация для большинства задач")
            elif motor_count == 6:
                recommendations.append("Гексакоптер - повышенная надежность и грузоподъемность")
            elif motor_count == 8:
                recommendations.append("Октокоптер - максимальная надежность и стабильность")

        return recommendations

    def save_report_to_file(self, report_text: str, filename: str = None):
        """
        Сохраняет отчет в текстовый файл

        Args:
            report_text: Текст отчета
            filename: Имя файла (если None, генерируется автоматически)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"drone_report_{timestamp}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_text)
        return filename