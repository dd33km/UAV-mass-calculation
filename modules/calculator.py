"""
Модуль расчета массы дрона.
Содержит логику валидации и вычисления общей массы конфигурации.
"""

from typing import Dict, Optional, Tuple


class DroneCalculator:
    """Класс для расчета массы дрона"""

    def __init__(self):
        """Инициализация калькулятора"""
        self.configuration = {}

    def validate_mass(self, mass: float) -> Tuple[bool, str]:
        """
        Проверяет корректность значения массы

        Args:
            mass: Значение массы для проверки

        Returns:
            Кортеж (валидность, сообщение об ошибке)
        """
        if mass < 0:
            return False, "Масса не может быть отрицательной"
        if mass > 50000:  # 50 кг максимум
            return False, "Масса слишком большая (максимум 50 кг)"
        return True, ""

    def validate_quantity(self, quantity: int) -> Tuple[bool, str]:
        """
        Проверяет корректность количества

        Args:
            quantity: Количество для проверки

        Returns:
            Кортеж (валидность, сообщение об ошибке)
        """
        if quantity < 0:
            return False, "Количество не может быть отрицательным"
        if quantity > 100:
            return False, "Количество слишком большое (максимум 100)"
        return True, ""

    def calculate_component_mass(self, component_mass: float, quantity: int = 1) -> float:
        """
        Вычисляет общую массу компонента с учетом количества

        Args:
            component_mass: Масса одного компонента
            quantity: Количество компонентов

        Returns:
            Общая масса компонентов
        """
        return component_mass * quantity

    def calculate_total_mass(self, components: Dict[str, Dict]) -> Dict:
        """
        Вычисляет общую массу дрона и разбивку по компонентам

        Args:
            components: Словарь с компонентами и их параметрами
                {
                    'frame': {'mass': float, 'qty': int, 'name': str},
                    'motor': {'mass': float, 'qty': int, 'name': str},
                    ...
                }

        Returns:
            Словарь с результатами расчета
        """
        results = {
            'components': {},
            'total_mass': 0.0,
            'component_count': 0
        }
        results = {
            'components': {},
            'total_mass': 0,
            'component_count': 0
        }

        for comp_type, comp_data in components.items():
            if comp_data and comp_data.get('mass') is not None:
                mass = comp_data['mass']
                qty = comp_data.get('qty', 1)
                total_comp_mass = self.calculate_component_mass(mass, qty)

                results['components'][comp_type] = {
                    'name': comp_data.get('name', 'Не выбран'),
                    'unit_mass': mass,
                    'quantity': qty,
                    'total_mass': total_comp_mass
                }

                results['total_mass'] += total_comp_mass
                results['component_count'] += 1

        return results

    def get_mass_distribution(self, components: Dict[str, Dict]) -> Dict[str, float]:
        """
        Получает распределение массы по компонентам для диаграммы

        Args:
            components: Словарь с компонентами

        Returns:
            Словарь {название_компонента: масса}
        """
        distribution = {}

        for comp_type, comp_data in components.items():
            if comp_data and comp_data.get('mass') is not None:
                name = comp_data.get('name', comp_type)
                qty = comp_data.get('qty', 1)
                total_mass = comp_data['mass'] * qty

                if qty > 1:
                    name = f"{name} (x{qty})"

                distribution[name] = total_mass

        return distribution

    def format_mass(self, mass: float) -> str:
        """
        Форматирует массу для отображения

        Args:
            mass: Масса в граммах

        Returns:
            Отформатированная строка
        """
        if mass >= 1000:
            return f"{mass / 1000:.2f} кг ({mass:.1f} г)"
        else:
            return f"{mass:.1f} г"

    def get_weight_category(self, total_mass: float) -> str:
        """
        Определяет категорию дрона по массе

        Args:
            total_mass: Общая масса в граммах

        Returns:
            Название категории
        """
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