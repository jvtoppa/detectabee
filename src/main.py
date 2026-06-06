#  Copyright (c) 2025 João Toppa <j213140@dac.unicamp.br>
 #  
 #   Redistribution and use in source and binary forms, with or without
 #   modification, are permitted provided that the following conditions
 #   are met:
 # 
 #   1. Redistributions of source code must retain the above Copyright
 #      notice, this list of conditions and the following disclaimer.
 #
 #   2. Redistributions in binary form must reproduce the above Copyright
 #      notice, this list of conditions and the following disclaimer in the
 #      documentation and/or other materials provided with the distribution.
 #
 #   3. Neither the name of the authors nor the names of its contributors
 #      may be used to endorse or promote products derived from this
 #      software without specific prior written permission.
 

# IMPORTS FOR PROBES

from RPi import GPIO
from board import SCL, SDA
import busio
import time
import adafruit_ssd1306
import adafruit_ccs811
import adafruit_bmp280
import configs
import sensors
import smbus
import camera
import tables 

# IMPORTS FOR BEE DETECTION

import cv2
import numpy as np

# SETUP - PROBES

i2c = busio.I2C(SCL, SDA)
bus = smbus.SMBus(1)

GPIO.setmode(GPIO.BCM)

ccs811 = adafruit_ccs811.CCS811(i2c)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, 0x76)
mpu9250 = sensors.Accelerometer(configs.DEVICE_ADDRESS, configs.ACCEL_XOUT_H, configs.ACCEL_CONFIG, bus, configs.PWR_MGMT_1)
sensors.Accelerometer.initialize(mpu9250)
probe = sensors.SensorProbe(ccs811, mpu9250, bmp280)

last_update_time = time.time()
update_interval = 0.4


camera_feed_db = tables.SQLiteTables("camera_feed", 5)
station_db = tables.SQLiteTables("station_feed", 1)

camera_main = camera.Camera(camera_feed_db, probe)

# MAIN LOOP

try:
    while True:
        current_time = time.time()
        if current_time - last_update_time >= update_interval:
            station_db.reading_and_writing_sensors([[0]], probe, current_time)
            last_update_time = current_time
        camera_main.capture()

finally:
    GPIO.cleanup()
    cv2.destroyAllWindows()