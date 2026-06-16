# 🐝 DetectaBee

**A computer vision-based bee monitoring system using ArUco markers and Raspberry Pi**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Research Project](https://img.shields.io/badge/Research-NEEPC--UFSCar-orange)](https://neepc.ufscar.br/)

## Overview

DetectaBee is an automated hive monitoring system that combines computer vision, environmental sensors, and embedded visualization to track bee activity and environmental conditions in real-time. Developed as part of a research project at NEEPC-UFSCar, this system uses ArUco marker detection to identify and monitor individual bees within a hive.

**Key Features:**
- 🎯 **ArUco Marker Detection** - Automated bee identification via computer vision
- 📊 **Environmental Monitoring** - Real-time temperature, pressure, acceleration, and air quality measurements
- 🔴 **Live Display** - OLED interface for instant data visualization
- 💾 **Data Logging** - Persistent storage of all measurements in CSV format
- ⚡ **Lightweight** - Optimized for Raspberry Pi 4 and above

## Hardware Requirements

### Essential Components
- **Raspberry Pi 4 (2GB RAM minimum, 4GB+ recommended)**
- **PiCamera2 or compatible camera module**
- **OLED Display (SSD1306, 128x64 resolution)**

### Sensors (Connected via I2C)
| Sensor | Function | I2C Address |
|--------|----------|-------------|
| **CCS811** | Air quality & CO₂ equivalent | 0x5A |
| **BMP280** | Temperature & barometric pressure | 0x76 |
| **MPU9250** | 3-axis accelerometer | 0x68 |

### Wiring
```
I2C Bus (GPIO 2 & 3):
  - CCS811 (Air Quality)
  - BMP280 (Temperature/Pressure)
  - MPU9250 (Accelerometer)
  
Camera:
  - CSI ribbon cable (auto-detected)
  
OLED Display:
  - I2C bus (same as sensors)
```

## Software Requirements

### System Dependencies
```bash
# Core packages
- Python 3.9+
- pip (Python package manager)
- git

# System libraries (install on Raspberry Pi OS)
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip libatlas-base-dev libjasper-dev
```

### Python Dependencies
See `requirements.txt` for complete list:
- `opencv-python` - Computer vision and ArUco marker detection
- `numpy` - Numerical computing
- `picamera2` - Raspberry Pi camera interface
- `adafruit-circuitpython-ccs811` - Air quality sensor driver
- `adafruit-circuitpython-bmp280` - Temperature/pressure sensor driver
- `adafruit-circuitpython-ssd1306` - OLED display driver
- `Pillow` - Image processing
- `smbus2` - I2C communication
- Additional: `board`, `busio`, `RPi.GPIO`, `RPi.bmp280`, `board`

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/jvtoppa/detectabee.git
cd detectabee
```

### 2. Enable Required Interfaces on Raspberry Pi
```bash
sudo raspi-config
# Enable: I2C, Camera, SPI
# Then reboot: sudo reboot
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Hardware Connection
```bash
# Check I2C devices
i2cdetect -y 1

# Test camera
libcamera-hello --list-cameras
```

### 5. Run the Application
```bash
chmod +x ./run.sh
./run.sh
```

Or directly:
```bash
python3 main.py
```

## Project Structure

```
detectabee/
├── main.py              # Main event loop and system integration
├── camera.py            # Camera capture and ArUco marker detection
├── sensors.py           # I2C sensor readings (CCS811, BMP280, MPU9250)
├── screen.py            # OLED display interface and rendering
├── tables.py            # Data management and CSV logging
├── configs.py           # Global configuration parameters
├── run.sh               # Startup script
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Configuration

### sensors.py
Configure sensor I2C addresses and calibration:
```python
CCS811_ADDR = 0x5A      # Air quality sensor
BMP280_ADDR = 0x76      # Temperature/pressure sensor
MPU9250_ADDR = 0x68     # Accelerometer
```

### camera.py
Adjust ArUco detection parameters:
```python
MARKER_SIZE = 0.05      # Expected marker size in meters
CAMERA_RESOLUTION = (1280, 720)
FPS = 30
```

### configs.py
Global settings:
- Data logging intervals
- Display refresh rate
- Sensor polling frequency
- CSV file output path

## Usage

### Starting the Monitor
```bash
python3 main.py
```

The system will:
1. Initialize all sensors
2. Start the camera feed
3. Display readings on the OLED screen
4. Log all measurements to CSV files

### Real-Time Data Visualization
- Environmental readings (temperature, pressure, CO₂) appear on the OLED display
- Detected bee markers are highlighted in the camera feed
- Data is continuously written to `data/` directory

### Stopping the Application
Press `Ctrl+C` to gracefully shutdown the system.

## Output Data

All measurements are logged to CSV files in the `data/` directory:

```
data/
├── hive_monitoring_YYYY-MM-DD.csv
├── sensor_readings_YYYY-MM-DD.csv
└── camera_detections_YYYY-MM-DD.csv
```

### CSV Format Example
```
timestamp,temperature,pressure,co2_equivalent,acceleration_x,acceleration_y,acceleration_z,bee_count,marker_ids
2026-06-16T10:30:45,25.3,1013.25,445,0.02,-0.01,1.00,5,"[12,15,23]"
```

## Troubleshooting

### Camera Issues
```bash
# Verify camera is detected
libcamera-hello --list-cameras

# Test camera feed
libcamera-jpeg -o test.jpg

# Solution: Ensure ribbon cable is firmly connected, enable camera in raspi-config
```

### I2C Sensor Not Found
```bash
# List connected I2C devices
i2cdetect -y 1

# If devices missing:
# 1. Check power (3.3V) to sensors
# 2. Verify SDA/SCL connections (GPIO 2 & 3)
# 3. Ensure pull-up resistors are installed (typically 10kΩ)
# 4. Check for duplicate addresses with: sudo dmesg
```

### OLED Display Blank
- Verify I2C address matches configuration (typically 0x3C or 0x3D)
- Check power supply (3.3V/5V depending on model)
- Test with: `sudo i2cdetect -y 1`

### Performance Issues
- Reduce camera resolution in `camera.py`
- Decrease sensor polling frequency in `configs.py`
- Close unnecessary background processes
- Use 4GB+ RAM Raspberry Pi

## Research & References

This project is part of ongoing research at **NEEPC-UFSCar** (Núcleo de Engenharia Eletrônica e Processamento de Computadores - Universidade Federal de São Carlos).

**Technologies Used:**
- OpenCV with ArUco marker detection
- Raspberry Pi embedded Linux
- I2C sensor integration
- Real-time data acquisition

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -m 'Add improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **NEEPC-UFSCar** - Research center providing project support
- **OpenCV Community** - ArUco marker detection library
- **Adafruit** - Sensor driver libraries
- **Raspberry Pi Foundation** - Hardware and documentation

## Citation

If you use DetectaBee in your research, please cite:

```bibtex
@software{detectabee2026,
  title={DetectaBee: Automated Hive Monitoring with ArUco Markers},
  author={Toppa, J. V.},
  year={2026},
  url={https://github.com/jvtoppa/detectabee},
  organization={NEEPC-UFSCar}
}
```

## Contact & Support

For issues, questions, or collaboration:
- 📧 Open a GitHub Issue
- 🔗 Visit [NEEPC-UFSCar](https://neepc.ufscar.br/)

---

**Made with 🐝 and ❤️ at UFSCar**
