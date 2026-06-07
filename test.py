import time
import board
import busio
import adafruit_am2320

print("--- Isolating AM2320 (0x5C) on I2C-1 ---")

# 1. Initialize Bus 1 only (Pins 3 and 5)
i2c1 = busio.I2C(board.SCL, board.SDA)

# 2. Initialize the sensor
try:
    am2320 = adafruit_am2320.AM2320(i2c1)
    print("Sensor object created successfully.")
except Exception as e:
    print(f"Initialization Failed: {e}")
    exit()

print("Starting read loop. Press Ctrl+C to exit.\n")

# 3. Dedicated Read Loop
while True:
    try:
        # The library automatically handles waking the chip up from deep sleep
        temp = am2320.temperature
        humidity = am2320.relative_humidity
        
        print(f"[{time.strftime('%H:%M:%S')}] Temp: {temp:.1f}°C | Humidity: {humidity:.1f}%")
        
    except OSError as e:
        # This catches common I2C bus timing/CRC issues if polled too quickly
        print(f"[{time.strftime('%H:%M:%S')}] Bus Read Warning: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
        
    # Crucial: Keep this delay at 3+ seconds. 
    # Polling the AM2320 faster than its sleep cycle causes it to lock up.
    time.sleep(3)