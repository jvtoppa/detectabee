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
                Probe_Location TEXT,
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
                Probe_Location TEXT,
                ID INTEGER,
                Temp_C REAL,
                Temp_F REAL,
                CO2 INTEGER,
                TVOC INTEGER,
                Vibration REAL
            """
            
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} ({columns_sql})")
        
        # Enhanced compound indexing for massive query performance improvements over time
        self.cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_time_loc_{self.table_name} ON {self.table_name} (Timestamp, Probe_Location);")
        self.conn.commit()

    def reading_and_writing_sensors(self, ids, probe_int, probe_ext, current_time, image_name=None):
        """Accepts both the internal (Bus 0) and external (Bus 1) sensor probes simultaneously."""
        if current_time - self.last_read_time >= self.read_interval:
            
            try:
                if hasattr(ids, 'flatten'):
                    resolved_id = int(ids.flatten()[0])
                elif isinstance(ids, list):
                    resolved_id = int(ids[0][0])
                else:
                    resolved_id = int(ids)
            except Exception:
                resolved_id = 0 

            timestamp = time.strftime('%Y-%m-%d-%H:%M:%S')

            probe_payloads = {
                "INT": probe_int,
                "EXT": probe_ext
            }

            for location, probe in probe_payloads.items():
                if probe is None:
                    continue  # Skip processing if a probe wasn't initialized
                
                temperature_c = probe.readTemperature()

                if not isinstance(temperature_c, str) and temperature_c is not None:
                    temperature_f = temperature_c * (9 / 5) + 32
                    temperature_c = round(temperature_c, 2)
                    temperature_f = round(temperature_f, 2)
                else:
                    temperature_c = None
                    temperature_f = None 

                co2 = probe.readECO2()
                tvoc = probe.readVolatile()
                vibration = probe.readAcceleration()
                
                co2 = None if co2 in ["None", "N/A", "none", "n/a"] else co2
                tvoc = None if tvoc in ["None", "N/A", "none", "n/a"] else tvoc
                vibration = None if vibration in ["None", "N/A", "none", "n/a"] else vibration

                if self.table_name == "camera_feed":
                    self.cursor.execute(
                        f"INSERT INTO {self.table_name} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (timestamp, location, resolved_id, image_name, temperature_c, temperature_f, co2, tvoc, vibration)
                    )
                else:
                    self.cursor.execute(
                        f"INSERT INTO {self.table_name} VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (timestamp, location, resolved_id, temperature_c, temperature_f, co2, tvoc, vibration)
                    )
            
            self.conn.commit()
            self.last_read_time = current_time

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()