import time
from time import sleep
import smbus2

print("--- Testing MPU9250 raw reads on i2c0 ---")

# 1. HARDWARE CONSTANTS
I2C_BUS_NUMBER = 0       # Targets /dev/i2c-0
DEVICE_ADDRESS = 0x68    # MPU9250 default I2C address
PWR_MGMT_1     = 0x6B
ACCEL_CONFIG   = 0x1C
ACCEL_XOUT_H   = 0x3B

# 2. FILTER GLOBAL VARIABLES (For tracking high-pass history)
alpha = 0.9
last_g = [0.0, 0.0, 0.0]
hp_g   = [0.0, 0.0, 0.0]

# 3. INITIALIZE BUS 0 AND DEVICE
# Opening via context manager handles clean file descriptors automatically
try:
    bus = smbus2.SMBus(I2C_BUS_NUMBER)
    
    # Wake up the MPU9250 (write 0 to power management register)
    bus.write_byte_data(DEVICE_ADDRESS, PWR_MGMT_1, 0x00)
    sleep(0.1)
    
    # Configure accelerometer setting (write 0 to configuration register)
    bus.write_byte_data(DEVICE_ADDRESS, ACCEL_CONFIG, 0x00)
    print("MPU9250 successfully initialized on i2c0.")
except Exception as e:
    print(f"Failed to open/initialize i2c0 hardware: {e}")
    exit(1)

# 4. RAW REGISTRY READ FUNCTION
def read_raw_register(addr):
    """Reads 2 sequential bytes from I2C and builds a signed 16-bit int."""
    high = bus.read_byte_data(DEVICE_ADDRESS, addr)
    low  = bus.read_byte_data(DEVICE_ADDRESS, addr + 1)
    
    # Combine high byte and low byte
    value = (high << 8) | low
    
    # Convert to signed integer
    if value > 32367:
        value -= 65536
    return value

# 5. VIBRATION PROCESSING FUNCTION
def get_vibration_reading():
    """Calculates high-pass filtered total vector vibration acceleration."""
    global last_g, hp_g
    axes_ms2 = [0.0, 0.0, 0.0]
    
    for i in range(3):
        # Reads sequential register pairs: X (0x3B), Y (0x3D), Z (0x3F)
        raw = read_raw_register(ACCEL_XOUT_H + (2 * i))
        
        # Convert raw counts to G forces (assuming +/- 2g scale factor)
        g_val = raw / 16384.0
        
        # Apply your high-pass filter math to strip out static gravity
        hp_g[i] = alpha * (hp_g[i] + g_val - last_g[i])
        last_g[i] = g_val
        
        # Convert Gs to meters per second squared
        axes_ms2[i] = hp_g[i] * 9.81
        
    # Calculate vector magnitude: sqrt(x^2 + y^2 + z^2)
    total_vibration = (axes_ms2[0]**2 + axes_ms2[1]**2 + axes_ms2[2]**2) ** 0.5
    return total_vibration

# 6. LIVE MONITORING LOOP
print("Streaming real-time vibration metrics. Press Ctrl+C to stop.\n")
try:
    while True:
        try:
            vib = get_vibration_reading()
            print(f"[{time.strftime('%H:%M:%S')}] MPU9250 Vibration: {vib:.4f} m/s²")
        except Exception as bus_err:
            print(f"[{time.strftime('%H:%M:%S')}] Bus 0 Communication Error: {bus_err}")
            
        time.sleep(0.4) # Polling rate matches your main architecture loop interval

except KeyboardInterrupt:
    print("\nTesting terminated safely.")
finally:
    bus.close()
    print("I2C-0 resource handle released.")