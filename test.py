import time
import board
import busio
import adafruit_ccs811
import adafruit_am2320
import adafruit_bmp280

print("--- Starting Dual I2C Connection Test ---")

# 1. Initialize Buses
# Bus 1 (Pins 3 and 5 for SDA1/SCL1)
i2c1 = busio.I2C(board.SCL, board.SDA)

# Bus 0 (Pins 27 and 28 for SDA0/SCL0 - ID_SD/ID_SC)
# Ensure 'dtparam=i2c_vc=on' is active in your /boot/firmware/config.txt
i2c0 = busio.I2C(board.D1, board.D0) 

# 2. Initialize Sensors on their respective buses
print("Connecting to sensors...")
#ccs_bus0 = adafruit_ccs811.CCS811(i2c0)
am2320 = adafruit_am2320.AM2320(i2c1)

ccs_bus1 = adafruit_ccs811.CCS811(i2c1)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c1, 0x76)

print("All sensors mapped successfully! Starting live read loop...\n")

# 3. Quick Read Loop
try:
    while True:
        print("="*50)
        print(f"TIME: {time.strftime('%H:%M:%S')}")
        
        # --- BUS 0 TEST ---
        print("\n[I2C-0 Bus Readings]")
        try:
            print(f"  CCS811 (Bus 0) -> eCO2: {ccs_bus0.eco2} ppm | TVOC: {ccs_bus0.tvoc} ppb")
        except Exception as e:
            print(f"  CCS811 (Bus 0) ERROR: {e}")
            
        try:
            print(f"  AM2320 (Bus 0) -> Temp: {am2320.temperature}°C | Hum: {am2320.relative_humidity}%")
        except Exception as e:
            print(f"  AM2320 (Bus 0) ERROR: {e}")

        # --- BUS 1 TEST ---
        print("\n[I2C-1 Bus Readings]")
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
