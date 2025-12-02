"""
Модуль графического интерфейса пользователя.
Создает современный интерфейс с использованием CustomTkinter.
"""

import customtkinter as ctk
from tkinter import messagebox, scrolledtext, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Dict, Optional
import os

from database.db_manager import DatabaseManager
from modules.calculator import DroneCalculator
from modules.visualizer import DroneVisualizer
from modules.report import ReportGenerator

# Настройка темы
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class DroneCalculatorGUI:
    """Главный класс GUI приложения"""

    def __init__(self):
        """Инициализация GUI"""
        self.root = ctk.CTk()
        self.root.title("Калькулятор массы дрона")
        self.root.geometry("1400x900")

        # Инициализация компонентов
        self.db = DatabaseManager()
        self.calculator = DroneCalculator()
        self.visualizer = DroneVisualizer()
        self.report_gen = ReportGenerator()

        # Хранилище выбранных компонентов
        self.selected_components = {
            'frame': None,
            'motor': None,
            'battery': None,
            'flight_controller': None,
            'propeller': None,
            'camera': None
        }

        # Хранилище виджетов
        self.component_widgets = {}
        self.quantity_widgets = {}

        # Создание интерфейса
        self._create_main_layout()
        self._create_calculator_tab()
        self._create_components_tab()
        self._create_history_tab()

        # Загрузка данных
        self._load_components_data()

    def _create_main_layout(self):
        """Создает основную структуру интерфейса"""
        # Заголовок
        header = ctk.CTkLabel(
            self.root,
            text="Калькулятор массы БПЛА",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        header.pack(pady=20)

        # Табы
        self.tabview = ctk.CTkTabview(self.root, width=1350, height=750)
        self.tabview.pack(pady=10, padx=20, fill="both", expand=True)

        # Создание вкладок
        self.tab_calculator = self.tabview.add("Калькулятор")
        self.tab_components = self.tabview.add("Управление компонентами")
        self.tab_history = self.tabview.add("История расчетов")

    def _create_calculator_tab(self):
        """Создает вкладку калькулятора"""
        # Основной контейнер с двумя колонками
        main_container = ctk.CTkFrame(self.tab_calculator)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Левая колонка - выбор компонентов
        left_frame = ctk.CTkFrame(main_container)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Заголовок
        ctk.CTkLabel(
            left_frame,
            text="Выбор компонентов",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        # Скроллируемый фрейм для компонентов
        scroll_frame = ctk.CTkScrollableFrame(left_frame, height=500)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Компоненты
        self._create_component_selector(scroll_frame, "frame", "Корпус", show_quantity=False)
        self._create_component_selector(scroll_frame, "motor", "Двигатели", show_quantity=True, default_qty=4)
        self._create_component_selector(scroll_frame, "battery", "Аккумулятор", show_quantity=False)
        self._create_component_selector(scroll_frame, "flight_controller", "Контроллер полета", show_quantity=False)
        self._create_component_selector(scroll_frame, "propeller", "Пропеллеры", show_quantity=True, default_qty=4)
        self._create_component_selector(scroll_frame, "camera", "Камера/Нагрузка", show_quantity=False)

        # Кнопки действий
        button_frame = ctk.CTkFrame(left_frame)
        button_frame.pack(pady=10, fill="x", padx=10)

        ctk.CTkButton(
            button_frame,
            text="Рассчитать массу",
            command=self._calculate_mass,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40
        ).pack(side="left", expand=True, padx=5)

        ctk.CTkButton(
            button_frame,
            text="Очистить",
            command=self._clear_selection,
            font=ctk.CTkFont(size=16),
            height=40,
            fg_color="gray"
        ).pack(side="left", expand=True, padx=5)

        # Правая колонка - результаты
        right_frame = ctk.CTkFrame(main_container)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Заголовок результатов
        ctk.CTkLabel(
            right_frame,
            text="Результаты расчета",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        # Общая масса
        self.total_mass_label = ctk.CTkLabel(
            right_frame,
            text="Общая масса: 0.0 г",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#4ECDC4"
        )
        self.total_mass_label.pack(pady=10)

        # Категория дрона
        self.category_label = ctk.CTkLabel(
            right_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color="#FFA07A"
        )
        self.category_label.pack(pady=5)

        # Фрейм для диаграммы
        self.chart_frame = ctk.CTkFrame(right_frame)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Кнопки для отчетов
        report_button_frame = ctk.CTkFrame(right_frame)
        report_button_frame.pack(pady=10, fill="x", padx=10)

        ctk.CTkButton(
            report_button_frame,
            text="Показать отчет",
            command=self._show_report,
            font=ctk.CTkFont(size=14),
            height=35
        ).pack(side="left", expand=True, padx=5)

        ctk.CTkButton(
            report_button_frame,
            text="Сохранить отчет",
            command=self._save_report,
            font=ctk.CTkFont(size=14),
            height=35
        ).pack(side="left", expand=True, padx=5)

    def _create_component_selector(self, parent, comp_type: str, label: str,
                                  show_quantity: bool = False, default_qty: int = 1):
        """Создает селектор для выбора компонента"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=5)

        # Заголовок
        ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=5)

        # Выпадающий список
        table_name = self._get_table_name(comp_type)
        components = self.db.get_components(table_name)
        component_names = ["Не выбран"] + [f"{c['name']} ({c['mass']}г)" for c in components]

        combobox = ctk.CTkComboBox(
            frame,
            values=component_names,
            width=400,
            font=ctk.CTkFont(size=14)
        )
        combobox.set("Не выбран")
        combobox.pack(padx=10, pady=5)

        self.component_widgets[comp_type] = {
            'combobox': combobox,
            'components': components
        }

        # Поле количества
        if show_quantity:
            qty_frame = ctk.CTkFrame(frame)
            qty_frame.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(
                qty_frame,
                text="Количество:",
                font=ctk.CTkFont(size=14)
            ).pack(side="left", padx=5)

            qty_entry = ctk.CTkEntry(
                qty_frame,
                width=100,
                font=ctk.CTkFont(size=14)
            )
            qty_entry.insert(0, str(default_qty))
            qty_entry.pack(side="left", padx=5)

            self.quantity_widgets[comp_type] = qty_entry

    def _get_table_name(self, comp_type: str) -> str:
        """Возвращает название таблицы для типа компонента"""
        table_map = {
            'frame': 'frames',
            'motor': 'motors',
            'battery': 'batteries',
            'flight_controller': 'flight_controllers',
            'propeller': 'propellers',
            'camera': 'cameras'
        }
        return table_map.get(comp_type, comp_type)

    def _calculate_mass(self):
        """Выполняет расчет массы"""
        try:
            # Собираем данные о выбранных компонентах
            components_data = {}

            for comp_type, widgets in self.component_widgets.items():
                combobox = widgets['combobox']
                selected = combobox.get()

                if selected != "Не выбран":
                    # Извлекаем ID компонента из списка
                    selected_index = combobox.cget("values").index(selected) - 1
                    if selected_index >= 0:
                        component = widgets['components'][selected_index]

                        # Получаем количество
                        qty = 1
                        if comp_type in self.quantity_widgets:
                            try:
                                qty = int(self.quantity_widgets[comp_type].get())
                                valid, msg = self.calculator.validate_quantity(qty)
                                if not valid:
                                    messagebox.showerror("Ошибка", f"{comp_type}: {msg}")
                                    return
                            except ValueError:
                                messagebox.showerror("Ошибка", f"Некорректное количество для {comp_type}")
                                return

                        components_data[comp_type] = {
                            'id': component['id'],
                            'name': component['name'],
                            'mass': component['mass'],
                            'qty': qty
                        }

            if not components_data:
                messagebox.showwarning("Предупреждение", "Выберите хотя бы один компонент")
                return

            # Выполняем расчет
            results = self.calculator.calculate_total_mass(components_data)

            # Обновляем отображение
            total_mass = results['total_mass']
            self.total_mass_label.configure(
                text=f"Общая масса: {self.calculator.format_mass(total_mass)}"
            )

            category = self.calculator.get_weight_category(total_mass)
            self.category_label.configure(text=f"Категория: {category}")

            # Создаем диаграмму
            distribution = self.calculator.get_mass_distribution(components_data)
            self._update_chart(distribution)

            # Сохраняем результаты для отчета
            self.last_calculation = {
                'results': results,
                'components_data': components_data
            }

            # Сохраняем в историю
            self._save_to_history(components_data, total_mass)

            messagebox.showinfo("Успех", "Расчет выполнен успешно!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при расчете: {str(e)}")

    def _update_chart(self, distribution: Dict[str, float]):
        """Обновляет диаграмму"""
        # Очищаем предыдущую диаграмму
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if not distribution:
            return

        # Создаем новую диаграмму
        fig = self.visualizer.create_pie_chart(distribution)

        # Встраиваем в tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _clear_selection(self):
        """Очищает выбор компонентов"""
        for widgets in self.component_widgets.values():
            widgets['combobox'].set("Не выбран")

        for entry in self.quantity_widgets.values():
            entry.delete(0, 'end')
            entry.insert(0, "1")

        self.total_mass_label.configure(text="Общая масса: 0.0 г")
        self.category_label.configure(text="")

        # Очищаем диаграмму
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

    # gui.py
    def _show_report(self):
        """Показывает текстовый отчет"""
        if not hasattr(self, 'last_calculation'):
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return

        try:

            report_text = self.report_gen.generate_text_report(
                self.last_calculation['results']
        )

        # Создаем окно с отчетом
            report_window = ctk.CTkToplevel(self.root)
            report_window.title("Отчет о массе БПЛА")
            report_window.geometry("600x600")

        # Текстовое поле с отчетом
            text_widget = ctk.CTkTextbox(
                report_window,
                font=ctk.CTkFont(family="Courier", size=12),
                wrap="none"
            )
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)
            text_widget.insert("1.0", report_text)
            text_widget.configure(state="disabled")

        # Кнопка закрытия
            ctk.CTkButton(
                report_window,
                text="Закрыть",
                command=report_window.destroy,
                height=35
            ).pack(pady=10)

        except Exception as e:

            messagebox.showerror("Ошибка генерации отчета", f"Не удалось создать отчет:\n{str(e)}")

    def _save_report(self):
        """Сохраняет отчет в файл"""
        if not hasattr(self, 'last_calculation'):
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return

        try:
            # Генерируем отчет
            report_text = self.report_gen.generate_text_report(
                self.last_calculation['results']
            )

            # Открываем диалог выбора места сохранения
            from datetime import datetime
            default_filename = f"drone_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=default_filename,
                title="Сохранить отчет"
            )

            # Если пользователь отменил сохранение
            if not filename:
                return

            # Сохраняем файл
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_text)

            messagebox.showinfo("Успех", f"Отчет успешно сохранен:\n{filename}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить отчет:\n{str(e)}")

    def _save_to_history(self, components_data: Dict, total_mass: float):
        """Сохраняет расчет в историю"""
        history_data = {'total_mass': total_mass}

        # Добавляем данные компонентов
        for comp_type, comp_data in components_data.items():
            prefix = comp_type
            history_data[f'{prefix}_id'] = comp_data['id']
            history_data[f'{prefix}_name'] = comp_data['name']
            history_data[f'{prefix}_mass'] = comp_data['mass']
            if 'qty' in comp_data:
                history_data[f'{prefix}_qty'] = comp_data['qty']

        self.db.save_calculation(history_data)

    def _create_components_tab(self):
        """Создает вкладку управления компонентами"""
        # Заголовок
        ctk.CTkLabel(
            self.tab_components,
            text="Управление базой компонентов",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        # Выбор типа компонента
        type_frame = ctk.CTkFrame(self.tab_components)
        type_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            type_frame,
            text="Тип компонента:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=10)

        self.component_type_var = ctk.StringVar(value="frames")
        component_types = {
            "Корпуса": "frames",
            "Двигатели": "motors",
            "Аккумуляторы": "batteries",
            "Контроллеры": "flight_controllers",
            "Пропеллеры": "propellers",
            "Камеры": "cameras"
        }

        for name, value in component_types.items():
            ctk.CTkRadioButton(
                type_frame,
                text=name,
                variable=self.component_type_var,
                value=value,
                command=self._load_components_list,
                font=ctk.CTkFont(size=12)
            ).pack(side="left", padx=5)

        # Список компонентов
        list_frame = ctk.CTkFrame(self.tab_components)
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.components_listbox = ctk.CTkTextbox(
            list_frame,
            font=ctk.CTkFont(family="Courier", size=12)
        )
        self.components_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Кнопки управления
        button_frame = ctk.CTkFrame(self.tab_components)
        button_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(
            button_frame,
            text="Добавить компонент",
            command=self._add_component_dialog,
            height=35
        ).pack(side="left", expand=True, padx=5)

        ctk.CTkButton(
            button_frame,
            text="Обновить список",
            command=self._load_components_list,
            height=35
        ).pack(side="left", expand=True, padx=5)

        # Загружаем начальный список
        self._load_components_list()

    def _load_components_list(self):
        """Загружает список компонентов выбранного типа"""
        table_name = self.component_type_var.get()
        components = self.db.get_components(table_name)

        self.components_listbox.configure(state="normal")
        self.components_listbox.delete("1.0", "end")

        header = f"{'ID':<5} {'Название':<30} {'Масса (г)':<12} {'Описание'}\n"
        self.components_listbox.insert("end", header)
        self.components_listbox.insert("end", "-" * 80 + "\n")

        for comp in components:
            line = f"{comp['id']:<5} {comp['name']:<30} {comp['mass']:<12.1f} {comp.get('description', '')}\n"
            self.components_listbox.insert("end", line)

        self.components_listbox.configure(state="disabled")

    def _add_component_dialog(self):
        """Открывает диалог добавления компонента"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Добавить компонент")
        dialog.geometry("500x400")

        # Поля ввода
        ctk.CTkLabel(dialog, text="Название:", font=ctk.CTkFont(size=14)).pack(pady=5)
        name_entry = ctk.CTkEntry(dialog, width=400)
        name_entry.pack(pady=5)

        ctk.CTkLabel(dialog, text="Масса (г):", font=ctk.CTkFont(size=14)).pack(pady=5)
        mass_entry = ctk.CTkEntry(dialog, width=400)
        mass_entry.pack(pady=5)

        ctk.CTkLabel(dialog, text="Описание:", font=ctk.CTkFont(size=14)).pack(pady=5)
        desc_entry = ctk.CTkEntry(dialog, width=400)
        desc_entry.pack(pady=5)

        def save_component():
            try:
                name = name_entry.get().strip()
                mass = float(mass_entry.get())
                description = desc_entry.get().strip()

                if not name:
                    messagebox.showerror("Ошибка", "Введите название")
                    return

                valid, msg = self.calculator.validate_mass(mass)
                if not valid:
                    messagebox.showerror("Ошибка", msg)
                    return

                table_name = self.component_type_var.get()
                self.db.add_component(table_name, {
                    'name': name,
                    'mass': mass,
                    'description': description
                })

                messagebox.showinfo("Успех", "Компонент добавлен")
                dialog.destroy()
                self._load_components_list()
                self._load_components_data()

            except ValueError:
                messagebox.showerror("Ошибка", "Некорректное значение массы")

        ctk.CTkButton(
            dialog,
            text="Сохранить",
            command=save_component,
            height=35
        ).pack(pady=20)

    def _create_history_tab(self):
        """Создает вкладку истории расчетов"""
        # Заголовок
        ctk.CTkLabel(
            self.tab_history,
            text="История расчетов",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        # Список истории
        list_frame = ctk.CTkFrame(self.tab_history)
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.history_listbox = ctk.CTkTextbox(
            list_frame,
            font=ctk.CTkFont(family="Courier", size=11)
        )
        self.history_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Кнопки
        button_frame = ctk.CTkFrame(self.tab_history)
        button_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(
            button_frame,
            text="Обновить",
            command=self._load_history,
            height=35
        ).pack(side="left", expand=True, padx=5)

        ctk.CTkButton(
            button_frame,
            text="Очистить историю",
            command=self._clear_history,
            height=35,
            fg_color="red"
        ).pack(side="left", expand=True, padx=5)

        # Загружаем историю
        self._load_history()

    def _load_history(self):
        """Загружает историю расчетов"""
        history = self.db.get_calculation_history()

        self.history_listbox.configure(state="normal")
        self.history_listbox.delete("1.0", "end")

        if not history:
            self.history_listbox.insert("end", "История расчетов пуста\n")
        else:
            for calc in history:
                self.history_listbox.insert("end", f"\n{'=' * 80}\n")
                self.history_listbox.insert("end", f"ID: {calc['id']} | Дата: {calc['timestamp']}\n")
                self.history_listbox.insert("end", f"Общая масса: {calc['total_mass']:.1f} г\n")
                self.history_listbox.insert("end", f"{'-' * 80}\n")

                if calc.get('frame_name'):
                    self.history_listbox.insert("end", f"Корпус: {calc['frame_name']} ({calc['frame_mass']}г)\n")
                if calc.get('motor_name'):
                    qty = calc.get('motor_qty', 1)
                    self.history_listbox.insert("end",
                                                f"Двигатели: {calc['motor_name']} x{qty} ({calc['motor_mass']}г)\n")
                if calc.get('battery_name'):
                    self.history_listbox.insert("end",
                                                f"Аккумулятор: {calc['battery_name']} ({calc['battery_mass']}г)\n")
                if calc.get('fc_name'):
                    self.history_listbox.insert("end", f"Контроллер: {calc['fc_name']} ({calc['fc_mass']}г)\n")
                if calc.get('propeller_name'):
                    qty = calc.get('propeller_qty', 1)
                    self.history_listbox.insert("end",
                                                f"Пропеллеры: {calc['propeller_name']} x{qty} ({calc['propeller_mass']}г)\n")
                if calc.get('camera_name'):
                    self.history_listbox.insert("end", f"Камера: {calc['camera_name']} ({calc['camera_mass']}г)\n")

        self.history_listbox.configure(state="disabled")

    def _clear_history(self):
        """Очищает историю расчетов"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            # Получаем все записи и удаляем их
            history = self.db.get_calculation_history(limit=1000)
            for calc in history:
                self.db.delete_calculation(calc['id'])

            self._load_history()
            messagebox.showinfo("Успех", "История очищена")

    def _load_components_data(self):
        """Перезагружает данные компонентов в выпадающих списках"""
        for comp_type, widgets in self.component_widgets.items():
            table_name = self._get_table_name(comp_type)
            components = self.db.get_components(table_name)
            component_names = ["Не выбран"] + [f"{c['name']} ({c['mass']}г)" for c in components]

            widgets['combobox'].configure(values=component_names)
            widgets['components'] = components

    def run(self):
        """Запускает приложение"""
        self.root.mainloop()