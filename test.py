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
        # Step 1: Manually force a wake-up signal down the bus
        try:
            i2c1.writeto(0x5C, b'')  # Send an empty byte to address 0x5C
        except OSError:
            # We EXPECT an error here because the sensor won't ACK while waking up
            pass
        
        # Step 2: Give its internal microcontroller a moment to boot up
        time.sleep(0.01)  # 10ms delay
        
        # Step 3: Now read the data normally
        temp = am2320.temperature
        humidity = am2320.relative_humidity
        
        print(f"[{time.strftime('%H:%M:%S')}] Temp: {temp:.1f}°C | Humidity: {humidity:.1f}%")
        
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Read failure: {e}")
        
    time.sleep(3)  # Keep the loop slow