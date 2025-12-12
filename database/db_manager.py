"""
Модуль управления базой данных SQLite для калькулятора массы дрона.
Содержит функции для работы с компонентами и историей расчетов.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    """Класс для управления базой данных дронов"""

    def __init__(self, db_path: str = "database/drone_components.db"):
        """
        Инициализация менеджера базы данных

        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
        self._ensure_database_exists()
        self._create_tables()
        self._populate_initial_data()

    def _ensure_database_exists(self):
        """Создает директорию для базы данных если её нет"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """Создает подключение к базе данных"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """Создает таблицы в базе данных"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Таблица корпусов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS frames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mass REAL NOT NULL,
                description TEXT
            )
        """)

        # Таблица двигателей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS motors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mass REAL NOT NULL,
                description TEXT
            )
        """)

        # Таблица аккумуляторов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batteries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mass REAL NOT NULL,
                capacity INTEGER,
                description TEXT
            )
        """)

        # Таблица контроллеров полета
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flight_controllers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mass REAL NOT NULL,
                description TEXT
            )
        """)

        # Таблица пропеллеров
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS propellers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mass REAL NOT NULL,
                size TEXT,
                description TEXT
            )
        """)

        # Таблица камер/полезной нагрузки
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cameras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mass REAL NOT NULL,
                description TEXT
            )
        """)

        # Таблица истории расчетов
        cursor.execute("DROP TABLE IF EXISTS calculations_history;")
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS calculations_history
                       (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,

        frame_id INTEGER,
        frame_name TEXT,
        frame_mass REAL,
        frame_qty INTEGER,

        motor_id INTEGER,
        motor_name TEXT,
        motor_mass REAL,
        motor_qty INTEGER,

        battery_id INTEGER,
        battery_name TEXT,
        battery_mass REAL,
        battery_qty INTEGER,

        flight_controller_id INTEGER,
        flight_controller_name TEXT,
        flight_controller_mass REAL,
        flight_controller_qty INTEGER,

        propeller_id INTEGER,
        propeller_name TEXT,
        propeller_mass REAL,
        propeller_qty INTEGER,

        camera_id INTEGER,
        camera_name TEXT,
        camera_mass REAL,
        camera_qty INTEGER, 

        total_mass REAL NOT NULL
                       );
                       """)

        conn.commit()
        conn.close()

    def _populate_initial_data(self):
        """Заполняет базу данных начальными данными"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Проверяем, есть ли уже данные
        cursor.execute("SELECT COUNT(*) FROM frames")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return

        # Корпуса
        frames_data = [
            ("DJI F450", 282, "Популярный квадрокоптер среднего размера"),
            ("DJI F550", 478, "Гексакоптер для тяжелой нагрузки"),
            ("Tarot 650", 520, "Складной карбоновый корпус"),
            ("ZMR250", 95, "Гоночный мини-квадрокоптер"),
            ("S500", 168, "Легкий корпус для FPV"),
        ]
        cursor.executemany(
            "INSERT INTO frames (name, mass, description) VALUES (?, ?, ?)",
            frames_data
        )

        # Двигатели
        motors_data = [
            ("DJI E305", 56, "920KV бесколлекторный двигатель"),
            ("T-Motor MN2214", 52, "920KV для мультикоптеров"),
            ("EMAX RS2205", 28, "2300KV гоночный двигатель"),
            ("SunnySky X2212", 47, "980KV универсальный"),
            ("Cobra 2213", 64, "1050KV мощный двигатель"),
        ]
        cursor.executemany(
            "INSERT INTO motors (name, mass, description) VALUES (?, ?, ?)",
            motors_data
        )

        # Аккумуляторы
        batteries_data = [
            ("Turnigy 3S 2200mAh", 185, 2200, "11.1V LiPo батарея"),
            ("Tattu 4S 5200mAh", 458, 5200, "14.8V высокая емкость"),
            ("ZOP 3S 1500mAh", 126, 1500, "11.1V легкая батарея"),
            ("Gens Ace 4S 4000mAh", 368, 4000, "14.8V для длительных полетов"),
            ("CNHL 6S 6000mAh", 682, 6000, "22.2V профессиональная"),
        ]
        cursor.executemany(
            "INSERT INTO batteries (name, mass, capacity, description) VALUES (?, ?, ?, ?)",
            batteries_data
        )

        # Контроллеры полета
        fc_data = [
            ("DJI Naza-M V2", 60, "GPS стабилизация"),
            ("Pixhawk 4", 38, "Открытый контроллер"),
            ("Betaflight F4", 8, "Для гоночных дронов"),
            ("APM 2.8", 45, "ArduPilot контроллер"),
            ("Holybro Kakute F7", 6, "Компактный F7 чип"),
        ]
        cursor.executemany(
            "INSERT INTO flight_controllers (name, mass, description) VALUES (?, ?, ?)",
            fc_data
        )

        # Пропеллеры
        propellers_data = [
            ("DJI 9450", 11, "9.4 inch", "Самозатягивающиеся пропеллеры"),
            ("Gemfan 5040", 4, "5 inch", "Карбоновые лопасти"),
            ("APC 10x4.7", 12, "10 inch", "Медленные полеты"),
            ("HQProp 6x4.5", 7, "6 inch", "Трехлопастные"),
            ("T-Motor 15x5", 28, "15 inch", "Для больших дронов"),
        ]
        cursor.executemany(
            "INSERT INTO propellers (name, mass, size, description) VALUES (?, ?, ?, ?)",
            propellers_data
        )

        # Камеры
        cameras_data = [
            ("GoPro Hero 11", 154, "Экшн-камера 5.3K"),
            ("DJI Zenmuse X5S", 461, "Профессиональная камера"),
            ("RunCam Split 4", 15, "FPV камера с записью 4K"),
            ("Foxeer Predator", 8, "Легкая FPV камера"),
            ("Sony A6000 + объектив", 450, "Беззеркальная камера"),
        ]
        cursor.executemany(
            "INSERT INTO cameras (name, mass, description) VALUES (?, ?, ?)",
            cameras_data
        )

        conn.commit()
        conn.close()

    def get_components(self, table_name: str) -> List[Dict]:
        """
        Получает все компоненты из указанной таблицы

        Args:
            table_name: Название таблицы

        Returns:
            Список словарей с данными компонентов
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def add_component(self, table_name: str, data: Dict) -> int:
        """
        Добавляет новый компонент в таблицу

        Args:
            table_name: Название таблицы
            data: Словарь с данными компонента

        Returns:
            ID добавленного компонента
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        cursor.execute(query, list(data.values()))
        component_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return component_id

    def update_component(self, table_name: str, component_id: int, data: Dict):
        """
        Обновляет данные компонента

        Args:
            table_name: Название таблицы
            component_id: ID компонента
            data: Словарь с новыми данными
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"

        cursor.execute(query, list(data.values()) + [component_id])
        conn.commit()
        conn.close()

    def delete_component(self, table_name: str, component_id: int):
        """
        Удаляет компонент из таблицы

        Args:
            table_name: Название таблицы
            component_id: ID компонента
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (component_id,))
        conn.commit()
        conn.close()

    def save_calculation(self, calculation_data: Dict) -> int:
        """
        Сохраняет расчет в историю

        Args:
            calculation_data: Словарь с данными расчета

        Returns:
            ID сохраненного расчета
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        calculation_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        columns = ', '.join(calculation_data.keys())
        placeholders = ', '.join(['?' for _ in calculation_data])
        query = f"INSERT INTO calculations_history ({columns}) VALUES ({placeholders})"

        cursor.execute(query, list(calculation_data.values()))
        calc_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return calc_id

    def get_calculation_history(self, limit: int = 50) -> List[Dict]:
        """
        Получает историю расчетов

        Args:
            limit: Максимальное количество записей

        Returns:
            Список расчетов
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM calculations_history ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def delete_calculation(self, calc_id: int):
        """
        Удаляет расчет из истории

        Args:
            calc_id: ID расчета
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM calculations_history WHERE id = ?", (calc_id,))
        conn.commit()
        conn.close()

    def get_component_by_id(self, table_name: str, component_id: int) -> Optional[Dict]:
        """
        Получает компонент по ID

        Args:
            table_name: Название таблицы
            component_id: ID компонента

        Returns:
            Словарь с данными компонента или None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (component_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None
