import RPi.GPIO as GPIO
import time
import signal
import sys
import os

from __init__ import db
from models import DataLog

# Initialization for PWM control
HUMIDIFIER_FAN_PWM_PIN = 16     # Pin used to control PWM fan
HUMIDIFIER_FAN_PWM_FREQ = 25    # [kHz] Frequency for PWM control

INTAKE_FAN_PWM_PIN = 0          # Pin used to control PWM fan
INTAKE_FAN_PWM_FREQ = 25        # [kHz] Frequency for PWM control

EXHAUST_FAN_PWM_PIN = 0         # Pin used to control PWM fan
EXHAUST_FAN_PWM_FREQ = 25       # [kHz] Frequency for PWM control

# Initialization for RPM feedback
HUMIDIFIER_FAN_RPM_PIN = 18     # Pin for RPM output
HUMIDIFER_FAN_RPM_PULSE = 2     # Pulses per fan revolution

INTAKE_FAN_RPM_PIN = 0          # Pin for RPM output
INTAKE_FAN_RPM_PULSE = 2        # Pulses per fan revolution

EXHAUST_FAN_RPM_PIN = 0         # Pin for RPM output
EXHAUST_FAN_RPM_PULSE = 2       # Pulses per fan revolution

# Parameters for temperature, humidity, and CO2 content control
MIN_TEMPERATURE = 68
TARGET_TEMPERATURE = 73         # [Degrees Fahrenheit]
MAX_TEMPERATURE = 78
TEMPERATURE_TOLERANCE_BAND = 0.045

MIN_HUMIDITY = 90
TARGET_HUMIDITY = 95            # [% Relative Humidity]
MAX_HUMIDITY = 100
HUMIDITY_TOLERANCE_BAND = 0.03

MIN_CO2_CONTENT = 400
TARGET_CO2_CONTENT = 600        # [Parts per Million CO2]
MAX_CO2_CONTENT = 800
CO2_TOLERANCE_BAND = 0.15

FAN_OFF = 0
FAN_LOW = 25
FAN_MID = 50
FAN_HIGH = 75
FAN_MAX = 100

STALL_TIME = 100                  # [sec] Controller sleep time



def set_fan_speed(target_fan, fan_speed):
    target_fan.start(fan_speed)
    return

def condition_analysis():
    # Temperature Control
    current_temperature = DataLog.query.order_by(DataLog.id.desc()).first().temperature


    # Humidity Control
    current_humidity = DataLog.query.order_by(DataLog.id.desc()).first().humidity


    # Carbon Dioxide Content Control
    current_carbon_dioxide = DataLog.query.order_by(DataLog.id.desc()).first().carbon_dioxide

    if current_carbon_dioxide >= MAX_CO2_CONTENT:
        set_fan_speed(humidifer_fan, FAN_MAX)
    elif current_carbon_dioxide >= TARGET_CO2_CONTENT * (1 + CO2_TOLERANCE_BAND) and current_carbon_dioxide < MAX_CO2_CONTENT:
        set_fan_speed(humidifer_fan, FAN_HIGH)
    elif current_carbon_dioxide <= TARGET_CO2_CONTENT * (1 - CO2_TOLERANCE_BAND) and current_carbon_dioxide > MIN_CO2_CONTENT:
        set_fan_speed(humidifer_fan, FAN_MID)
    elif current_carbon_dioxide <= MIN_CO2_CONTENT:
        set_fan_speed(humidifer_fan, FAN_LOW)
    else:
        set_fan_speed(humidifer_fan, FAN_MID)

try:
    # Initialize PWM fan control
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(HUMIDIFIER_FAN_PWM_PIN, GPIO.OUT, initial=GPIO.LOW)
    # GPIO.setup(INTAKE_FAN_PWM_PIN, GPIO.OUT, initial=GPIO.LOW)
    # GPIO.setup(EXHAUST_FAN_PWM_PIN, GPIO.OUT, initial=GPIO.LOW)
    humidifer_fan = GPIO.PWM(HUMIDIFIER_FAN_PWM_PIN, HUMIDIFIER_FAN_PWM_FREQ)
    # intake_fan = GPIO.PWM(INTAKE_FAN_PWM_PIN, INTAKE_FAN_PWM_FREQ)
    # exhaust_fan = GPIO.PWM(EXHAUST_FAN_PWM_PIN, EXHAUST_FAN_PWM_FREQ)
    set_fan_speed(humidifer_fan, FAN_OFF)
    # set_fan_speed(intake_fan, FAN_OFF)
    # set_fan_speed(exhaust_fan, FAN_OFF)

    # Realtime fan control
    while True:
        condition_analysis()
        time.sleep(STALL_TIME)

except KeyboardInterrupt:
    set_fan_speed(humidifer_fan, FAN_HIGH)
    # set_fan_speed(intake_fan, FAN_HIGH)
    # set_fan_speed(exhaust_fan, FAN_HIGH)