import configs
import time
import os
import sqlite3

class SQLiteTables:

    def __init__(self, typ, interval):
        self.pathDB = configs.path_to_folder + typ + ".db"
        self.table_name = typ
        self.last_read_time = 0
        self.read_interval = interval
        self.initialize()

    def initialize(self):
        target_dir = os.path.dirname(self.pathDB)
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            
        self.conn = sqlite3.connect(self.pathDB)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA journal_mode=WAL;")
        
        if self.table_name == "camera_feed":
            columns_sql = """
                Timestamp TEXT,
                ID INTEGER,
                Image_Path TEXT,
                Temp_C REAL,
                Temp_F REAL,
                CO2 INTEGER,
                TVOC INTEGER,
                Vibration REAL
            """
        else:
            columns_sql = """
                Timestamp TEXT,
                ID INTEGER,
                Temp_C REAL,
                Temp_F REAL,
                CO2 INTEGER,
                TVOC INTEGER,
                Vibration REAL
            """
            
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} ({columns_sql})")
        
        self.cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_timestamp_{self.table_name} ON {self.table_name} (Timestamp);")
        self.conn.commit()

    def reading_and_writing_sensors(self, ids, probe, current_time, image_name=None):
        if current_time - self.last_read_time >= self.read_interval:
            temperature_c = probe.readTemperature()

            if not isinstance(temperature_c, str):
                temperature_f = temperature_c * (9 / 5) + 32
                temperature_c = round(temperature_c, 2)
                temperature_f = round(temperature_f, 2)
            else:
                temperature_f = None 

            co2 = probe.readECO2()
            tvoc = probe.readVolatile()
            vibration = probe.readAcceleration()
            
            co2 = None if co2 in ["None", "N/A", "none", "n/a"] else co2
            tvoc = None if tvoc in ["None", "N/A", "none", "n/a"] else tvoc

            timestamp = time.strftime('%Y-%m-%d-%H:%M:%S')

            if self.table_name == "camera_feed":
                self.cursor.execute(
                    f"INSERT INTO {self.table_name} VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (timestamp, ids[0][0], image_name, temperature_c, temperature_f, co2, tvoc, vibration)
                )
            else:
                self.cursor.execute(
                    f"INSERT INTO {self.table_name} VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (timestamp, ids[0][0], temperature_c, temperature_f, co2, tvoc, vibration)
                )
            
            self.conn.commit()
            self.last_read_time = current_time

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()