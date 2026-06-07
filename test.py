import time
import board
import busio
import adafruit_ccs811
import adafruit_am2320
import adafruit_bmp280
import adafruit_mpu6050  # Pure CircuitPython driver instead of smbus

print("--- Starting Pure Busio Dual I2C Connection Test ---")

# 1. Initialize Buses
# Bus 1 (Pins 3 and 5 for SDA1/SCL1)
i2c1 = busio.I2C(board.SCL, board.SDA)

# Bus 0 (Pins 27 and 28 for SDA0/SCL0 - ID_SD/ID_SC)
i2c0 = busio.I2C(board.D1, board.D0) 

# 2. Initialize Sensors on their respective buses
print("Connecting to sensors...")

# --- SENSORS ON BUS 0 (i2c0) ---
try:
    # This targets address 0x68 on the i2c0 bus object
    mpu = adafruit_mpu6050.MPU6050(i2c0)
    print("  MPU sensor initialized on i2c0.")
except Exception as e:
    print(f"  Failed to initialize MPU on i2c0: {e}")
    mpu = None

# --- SENSORS ON BUS 1 (i2c1) ---
am2320 = adafruit_am2320.AM2320(i2c1)
ccs_bus1 = adafruit_ccs811.CCS811(i2c1)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c1, 0x76)

print("Mapping sequence complete! Starting live read loop...\n")

# 3. Quick Read Loop
try:
    while True:
        print("="*50)
        print(f"TIME: {time.strftime('%H:%M:%S')}")
        
        # --- BUS 0 TEST ---
        print("\n[I2C-0 Bus Readings]")
        if mpu:
            try:
                # Read acceleration data vector (X, Y, Z in m/s^2)
                accel_x, accel_y, accel_z = mpu.acceleration
                
                # Calculate the magnitude of the total acceleration vector
                vibration = (accel_x**2 + accel_y**2 + accel_z**2) ** 0.5
                print(f"  MPU (i2c0) -> Total Acceleration: {vibration:.4f} m/s²")
            except Exception as e:
                print(f"  MPU (i2c0) ERROR: {e}")
        else:
            print("  MPU (i2c0) -> Skipping (Not Initialized)")

        # --- BUS 1 TEST ---
        print("\n[I2C-1 Bus Readings]")
        try:
            print(f"  AM2320 (Bus 1) -> Temp: {am2320.temperature}°C%")
        except Exception as e:
            print(f"  AM2320 (Bus 1) ERROR: {e}")

        try:
            print(f"  CCS811 (Bus 1) -> eCO2: {ccs_bus1.eco2} ppm | TVOC: {ccs_bus1.tvoc} ppb")
        except Exception as e:
            print(f"  CCS811 (Bus 1) ERROR: {e}")
            
        try:
            print(f"  BMP280 (Bus 1) -> Temp: {bmp280.temperature}°C")
        except Exception as e:
            print(f"  BMP280 (Bus 1) ERROR: {e}")

        time.sleep(2)

except KeyboardInterrupt:
    print("\nTest stopped by user.")