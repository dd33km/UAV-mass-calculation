"""
Модуль визуализации данных.
Создает графики и диаграммы для отображения распределения массы.
"""

import matplotlib

matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from typing import Dict
import os

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    FigureCanvasTkAgg = None


class DroneVisualizer:
    """Класс для визуализации данных о массе дрона"""

    def __init__(self):
        """Инициализация визуализатора"""
        # Настройка стиля matplotlib
        plt.style.use('dark_background')
        self.colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
            '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2'
        ]

    def create_pie_chart(self, data: Dict[str, float], title: str = "Распределение массы дрона") -> plt.Figure:
        """
        Создает круговую диаграмму распределения массы

        Args:
            data: Словарь {компонент: масса}
            title: Заголовок диаграммы

        Returns:
            Figure объект matplotlib
        """
        if not data:
            # Создаем пустую диаграмму
            fig, ax = plt.subplots(figsize=(8, 6), facecolor='#2b2b2b')
            ax.text(0.5, 0.5, 'Нет данных для отображения',
                    ha='center', va='center', fontsize=14, color='white')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig

        # Создаем диаграмму
        fig, ax = plt.subplots(figsize=(6, 4), facecolor='#2b2b2b')

        labels = list(data.keys())
        sizes = list(data.values())

        # Функция для форматирования процентов и массы
        def make_autopct(values):
            def my_autopct(pct):
                total = sum(values)
                val = pct * total / 100.0
                return f'{pct:.1f}%\n({val:.1f}г)'

            return my_autopct

        # Создаем круговую диаграмму
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=self.colors[:len(labels)],
            autopct=make_autopct(sizes),
            startangle=90,
            textprops={'color': 'white', 'fontsize': 10}
        )

        # Улучшаем читаемость процентов
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_weight('bold')

        # Заголовок
        ax.set_title(title, color='white', fontsize=14, fontweight='bold', pad=20)

        # Равные пропорции для круга
        ax.axis('equal')

        plt.tight_layout()
        return fig

    def create_bar_chart(self, data: Dict[str, float], title: str = "Масса компонентов") -> plt.Figure:
        """
        Создает столбчатую диаграмму массы компонентов

        Args:
            data: Словарь {компонент: масса}
            title: Заголовок диаграммы

        Returns:
            Figure объект matplotlib
        """
        if not data:
            fig, ax = plt.subplots(figsize=(8, 6), facecolor='#2b2b2b')
            ax.text(0.5, 0.5, 'Нет данных для отображения',
                    ha='center', va='center', fontsize=14, color='white')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig

        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2b2b2b')
        ax.set_facecolor('#2b2b2b')

        components = list(data.keys())
        masses = list(data.values())

        bars = ax.bar(components, masses, color=self.colors[:len(components)])

        # Добавляем значения над столбцами
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height:.1f}г',
                    ha='center', va='bottom', color='white', fontsize=10)

        ax.set_xlabel('Компоненты', color='white', fontsize=12)
        ax.set_ylabel('Масса (г)', color='white', fontsize=12)
        ax.set_title(title, color='white', fontsize=14, fontweight='bold')

        # Поворачиваем подписи по оси X для лучшей читаемости
        plt.xticks(rotation=45, ha='right', color='white')
        plt.yticks(color='white')

        # Настройка сетки
        ax.grid(True, alpha=0.3, color='gray', linestyle='--')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        return fig

    def embed_figure_in_tkinter(self, figure: plt.Figure, parent_frame):
        """
        Встраивает matplotlib figure в tkinter frame

        Args:
            figure: Matplotlib figure
            parent_frame: Родительский tkinter frame

        Returns:
            Canvas объект или None если tkinter недоступен
        """
        if not TKINTER_AVAILABLE or FigureCanvasTkAgg is None:
            return None

        canvas = FigureCanvasTkAgg(figure, master=parent_frame)
        canvas.draw()

        return canvas
