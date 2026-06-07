import time
from time import sleep
import board
import busio
import smbus2
import adafruit_ccs811
import adafruit_am2320
import adafruit_bmp280 # Works perfectly for BME280 temperature tracking

print("==================================================")
print("       CORRECTED DUAL I2C BUS TEST BENCH         ")
print("==================================================")

# ----------------------------------------------------------------
# 1. INITIALIZE HARDWARE BUSES
# ----------------------------------------------------------------
print("Initializing I2C buses...")

# Bus 1: Default hardware pins (SDA1/SCL1)
i2c1 = busio.I2C(board.SCL, board.SDA)

# Bus 0: Secondary hardware pins (SDA0/SCL0)
i2c0 = busio.I2C(board.D1, board.D0) 
bus0_raw = smbus2.SMBus(0) # Raw handle for the MPU9250 on Bus 0

# ----------------------------------------------------------------
# 2. MPU9250 CONFIGURATION & CONSTANTS (I2C-0)
# ----------------------------------------------------------------
MPU_ADDR       = 0x68
PWR_MGMT_1     = 0x6B
ACCEL_CONFIG   = 0x1C
ACCEL_XOUT_H   = 0x3B

alpha = 0.9
last_g = [0.0, 0.0, 0.0]
hp_g   = [0.0, 0.0, 0.0]

def init_mpu9250():
    try:
        bus0_raw.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0x00)
        sleep(0.1)
        bus0_raw.write_byte_data(MPU_ADDR, ACCEL_CONFIG, 0x00)
        return True
    except Exception as e:
        print(f" [!] MPU9250 HW Init Error: {e}")
        return False

def read_raw_mpu(addr):
    high = bus0_raw.read_byte_data(MPU_ADDR, addr)
    low  = bus0_raw.read_byte_data(MPU_ADDR, addr + 1)
    value = (high << 8) | low
    if value > 32767:
        value -= 65536
    return value

def get_vibration():
    global last_g, hp_g
    axes_ms2 = [0.0, 0.0, 0.0]
    for i in range(3):
        raw = read_raw_mpu(ACCEL_XOUT_H + (2 * i))
        g_val = raw / 16384.0
        hp_g[i] = alpha * (hp_g[i] + g_val - last_g[i])
        last_g[i] = g_val
        axes_ms2[i] = hp_g[i] * 9.81
    return (axes_ms2[0]**2 + axes_ms2[1]**2 + axes_ms2[2]**2) ** 0.5

# ----------------------------------------------------------------
# 3. INITIALIZE SENSORS BASED ON YOUR LAYOUT
# ----------------------------------------------------------------
print("\nConnecting to your layout...")

# --- SENSORS ON BUS 1 (i2c1) ---
try:
    ccs_bus1 = adafruit_ccs811.CCS811(i2c1)
    print(" [+] CCS811 detected on i2c1 (0x5A)")
except Exception as e:
    print(f" [-] CCS811 on i2c1 Failed: {e}")
    ccs_bus1 = None

try:
    am2320 = adafruit_am2320.AM2320(i2c1)
    print(" [+] AM2320 detected on i2c1 (0x5C)")
except Exception as e:
    print(f" [-] AM2320 on i2c1 Failed: {e}")
    am2320 = None


# --- SENSORS ON BUS 0 (i2c0) ---
try:
    ccs_bus0 = adafruit_ccs811.CCS811(i2c0)
    print(" [+] CCS811 detected on i2c0 (0x5A)")
except Exception as e:
    print(f" [-] CCS811 on i2c0 Failed: {e}")
    ccs_bus0 = None

try:
    bme280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c0, 0x76)
    print(" [+] BME280 detected on i2c0 (0x76)")
except Exception as e:
    print(f" [-] BME280 on i2c0 Failed: {e}")
    bme280 = None

mpu_active = init_mpu9250()
if mpu_active:
    print(" [+] MPU9250 detected on i2c0 (0x68)")

print("\nSetup configuration loaded. Starting live loop...\n")

# ----------------------------------------------------------------
# 4. MONITORING LOOP
# ----------------------------------------------------------------
try:
    while True:
        print("-" * 60)
        print(f"TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # ====== I2C-0 READINGS ======
        print("\n [I2C-0 BUS DATA]")
        if ccs_bus0:
            try:
                print(f"   CCS811       -> eCO2: {ccs_bus0.eco2} ppm | TVOC: {ccs_bus0.tvoc} ppb")
            except Exception as e:
                print(f"   CCS811 Error -> {e}")
        else:
            print("   CCS811       -> OFFLINE")

        if bme280:
            try:
                print(f"   BME280 Temp  -> {bme280.temperature:.2f} °C")
            except Exception as e:
                print(f"   BME280 Error -> {e}")
        else:
            print("   BME280       -> OFFLINE")

        if mpu_active:
            try:
                print(f"   MPU9250 Vib  -> {get_vibration():.4f} m/s²")
            except Exception as e:
                print(f"   MPU9250 Error -> {e}")
        else:
            print("   MPU9250      -> OFFLINE")