import RPi.GPIO as GPIO
import time
from importlib import reload

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

STALL_TIME = 50                  # [sec] Controller sleep time



def set_fan_speed(target_fan, fan_speed):
    target_fan.start(fan_speed)
    return

def fan_control():    
    # Temperature Control
    current_temperature = DataLog.query.order_by(DataLog.id.desc()).first().temperature


    # Humidity Control
    current_humidity = DataLog.query.order_by(DataLog.id.desc()).first().humidity


    # Carbon Dioxide Content Control
    current_carbon_dioxide = DataLog.query.order_by(DataLog.id.desc()).first().carbon_dioxide

    if current_carbon_dioxide >= MAX_CO2_CONTENT:
        set_fan_speed(humidifer_fan, FAN_MAX)
        print(f'CARBON DIOXIDE READING OF {current_carbon_dioxide} - SETTING HUMIDIFER FAN SPEED TO {FAN_MAX}%')
    elif current_carbon_dioxide >= TARGET_CO2_CONTENT * (1 + CO2_TOLERANCE_BAND) and current_carbon_dioxide < MAX_CO2_CONTENT:
        set_fan_speed(humidifer_fan, FAN_HIGH)
        print(f'CARBON DIOXIDE READING OF {current_carbon_dioxide} - SETTING HUMIDIFER FAN SPEED TO {FAN_HIGH}%')
    elif current_carbon_dioxide <= TARGET_CO2_CONTENT * (1 - CO2_TOLERANCE_BAND) and current_carbon_dioxide > MIN_CO2_CONTENT:
        set_fan_speed(humidifer_fan, FAN_MID)
        print(f'CARBON DIOXIDE READING OF {current_carbon_dioxide} - SETTING HUMIDIFER FAN SPEED TO {FAN_MID}%')
    elif current_carbon_dioxide <= MIN_CO2_CONTENT:
        set_fan_speed(humidifer_fan, FAN_LOW)
        print(f'CARBON DIOXIDE READING OF {current_carbon_dioxide} - SETTING HUMIDIFER FAN SPEED TO {FAN_LOW}%')
    else:
        set_fan_speed(humidifer_fan, FAN_MID)
        print(f'CARBON DIOXIDE READING OF {current_carbon_dioxide} - SETTING HUMIDIFER FAN SPEED TO {FAN_MID}%')

def read_fan_speed(fan, pulse):
    dt = time.time() - initial_time
    if dt < 0.005:
        return

    frequency = 1 / dt
    rpm = (frequency / pulse) * 60
    print(f'{fan} fan speed = {rpm} RPM')
    initial_time = time.time()

try:
    print('Initializing control...')
    # Initialize PWM fan control
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(HUMIDIFIER_FAN_PWM_PIN, GPIO.OUT, initial=GPIO.LOW)
    # GPIO.setup(INTAKE_FAN_PWM_PIN, GPIO.OUT, initial=GPIO.LOW)
    # GPIO.setup(EXHAUST_FAN_PWM_PIN, GPIO.OUT, initial=GPIO.LOW)

    GPIO.setup(HUMIDIFIER_FAN_RPM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # GPIO.setup(INTAKE_FAN_RPM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # GPIO.setup(EXHAUST_FAN_RPM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    humidifer_fan = GPIO.PWM(HUMIDIFIER_FAN_PWM_PIN, HUMIDIFIER_FAN_PWM_FREQ)
    # intake_fan = GPIO.PWM(INTAKE_FAN_PWM_PIN, INTAKE_FAN_PWM_FREQ)
    # exhaust_fan = GPIO.PWM(EXHAUST_FAN_PWM_PIN, EXHAUST_FAN_PWM_FREQ)

    set_fan_speed(humidifer_fan, FAN_OFF)
    # set_fan_speed(intake_fan, FAN_OFF)
    # set_fan_speed(exhaust_fan, FAN_OFF)

    # Fan RPM data collection
    initial_time = time.time()
    GPIO.add_event_detect(HUMIDIFIER_FAN_RPM_PIN, GPIO.BOTH)
    # GPIO.add_event_detect(INTAKE_FAN_RPM_PIN, GPIO.BOTH)
    # GPIO.add_event_detect(EXHAUST_FAN_RPM_PIN, GPIO.BOTH)



    # Realtime control
    while True:
        reload(__init__)
        reload(models)

        fan_control()

        initial_time = time.time()
        if GPIO.event_detected(HUMIDIFIER_FAN_RPM_PIN):
            read_fan_speed('Humidifier', HUMIDIFER_FAN_RPM_PULSE)
    
        if GPIO.event_detected(INTAKE_FAN_RPM_PIN):
            read_fan_speed('Intake', INTAKE_FAN_RPM_PULSE)

        if GPIO.event_detected(EXHAUST_FAN_RPM_PIN):
            read_fan_speed('Exhaust', EXHAUST_FAN_RPM_PULSE)

        time.sleep(STALL_TIME)

except KeyboardInterrupt:
    print(f'''
        CANCELLED CONTROL:
        SETTING HUMIDIFIER FAN SPEED TO {FAN_HIGH}%
        SETTING INTAKE FAN SPEED TO {FAN_HIGH}%
        SETTING EXHAUST FAN SPEED TO {FAN_HIGH}%
    ''')
    set_fan_speed(humidifer_fan, FAN_HIGH)
    # set_fan_speed(intake_fan, FAN_HIGH)
    # set_fan_speed(exhaust_fan, FAN_HIGH)
    GPIO.cleanup()