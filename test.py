import time
from time import sleep
import board
import busio
import smbus2
import adafruit_ccs811
import adafruit_am2320
import adafruit_bmp280

print("==================================================")
print("       ALL-IN-ONE DUAL I2C BUS TEST BENCH         ")
print("==================================================")

# ----------------------------------------------------------------
# 1. INITIALIZE HARDWARE BUSES
# ----------------------------------------------------------------
print("Initializing I2C buses...")

# Bus 1: Default hardware pins (SDA1/SCL1)
i2c1 = busio.I2C(board.SCL, board.SDA)

# Bus 0: Secondary hardware pins (SDA0/SCL0)
# Ensure 'dtparam=i2c_vc=on' is in your /boot/firmware/config.txt
i2c0 = busio.I2C(board.D1, board.D0) 
bus0_raw = smbus2.SMBus(0) # Open raw smbus handle for MPU9250 on bus 0

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
    high = bus0_raw.write_byte_data(MPU_ADDR, addr, 0x00) # Ensure active wake
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
# 3. INITIALIZE ALL INSTANCES
# ----------------------------------------------------------------
print("Connecting to sensor layout...")

# --- BUS 0 SENSORS ---
mpu_active = init_mpu9250()

try:
    am2320 = adafruit_am2320.AM2320(i2c0)
    print(" [+] AM2320 detected on i2c0")
except Exception as e:
    print(f" [-] AM2320 Initialization Failed: {e}")
    am2320 = None

# --- BUS 1 SENSORS ---
try:
    ccs_bus1_A = adafruit_ccs811.CCS811(i2c1) # Defaults to 0x5A
    print(" [+] CCS811 (A) detected on i2c1 (0x5A)")
except Exception as e:
    print(f" [-] CCS811 (A) Failed: {e}")
    ccs_bus1_A = None

try:
    # If your second board is modified to 0x5B, use this layout:
    ccs_bus1_B = adafruit_ccs811.CCS811(i2c1, address=0x5B)
    print(" [+] CCS811 (B) detected on i2c1 (0x5B)")
except Exception as e:
    print(f" [-] CCS811 (B) Failed (Check address jumpers): {e}")
    ccs_bus1_B = None

try:
    bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c1, 0x76)
    print(" [+] BMP280 detected on i2c1 (0x76)")
except Exception as e:
    print(f" [-] BMP280 Failed: {e}")
    bmp280 = None

print("\nSetup complete. Commencing streaming data frame...\n")

# ----------------------------------------------------------------
# 4. MONITORING LOOP
# ----------------------------------------------------------------
try:
    while True:
        print("-" * 60)
        print(f"TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # ====== I2C-0 READINGS ======
        print("\n [I2C-0 BUS DATA]")
        
        if mpu_active:
            try:
                print(f"   MPU9250 Vib  -> {get_vibration():.4f} m/s²")
            except Exception as e:
                print(f"   MPU9250 Error -> {e}")
        else:
            print("   MPU9250      -> OFFLINE")

        if am2320:
            try:
                # Manual empty write to pop AM2320 out of state sleep
                try: i2c0.writeto(0x5C, b'')
                except: pass
                time.sleep(0.01)
                
                print(f"   AM2320 Temp  -> {am2320.temperature:.2f} °C")
                print(f"   AM2320 Hum   -> {am2320.relative_humidity:.2f} %")
            except Exception as e:
                print(f"   AM2320 Error -> {e}")
        else:
            print("   AM2320       -> OFFLINE")

        # ====== I2C-1 READINGS ======
        print("\n [I2C-1 BUS DATA]")
        
        if ccs_bus1_A:
            try:
                print(f"   CCS811 (0x5A)-> eCO2: {ccs_bus1_A.eco2} ppm | TVOC: {ccs_bus1_A.tvoc} ppb")
            except Exception as e:
                print(f"   CCS811 (0x5A)-> Error: {e}")
        else:
            print("   CCS811 (0x5A)-> OFFLINE")

        if ccs_bus1_B:
            try:
                print(f"   CCS811 (0x5B)-> eCO2: {ccs_bus1_B.eco2} ppm | TVOC: {ccs_bus1_B.tvoc} ppb")
            except Exception as e:
                print(f"   CCS811 (0x5B)-> Error: {e}")
        else:
            print("   CCS811 (0x5B)-> OFFLINE / NOT CONFIG")

        if bmp280:
            try:
                print(f"   BMP280 Temp  -> {bmp280.temperature:.2f} °C")
            except Exception as e:
                print(f"   BMP280 Error -> {e}")
        else:
            print("   BMP280       -> OFFLINE")

        # 3 seconds prevents data bus buffer overflows from the slow AM2320 response times
        time.sleep(3)

except KeyboardInterrupt:
    print("\nBenchmark sequence aborted by operator.")
finally:
    bus0_raw.close()
    print("Hardware handles detached.")