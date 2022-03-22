import time
import datetime
import board
import adafruit_dht
import mh_z19
import RPi.GPIO as GPIO

from __init__ import db
from models import DataLog, DataLogHistorical

# Initialize runtime parameters
dht_device = adafruit_dht.DHT22(board.D4)
sampling_frequency = 100.0

# Initialization for PWM control
HUMIDIFIER_FAN_PWM_PIN = 23     # Pin used to control PWM fan
HUMIDIFIER_FAN_PWM_FREQ = 25    # [Hz] Frequency for PWM control

INTAKE_FAN_PWM_PIN = 27         # Pin used to control PWM fan
INTAKE_FAN_PWM_FREQ = 25        # [Hz] Frequency for PWM control

EXHAUST_FAN_PWM_PIN = 5         # Pin used to control PWM fan
EXHAUST_FAN_PWM_FREQ = 25       # [Hz] Frequency for PWM control

# Initialization for RPM feedback
HUMIDIFIER_FAN_RPM_PIN = 24     # Pin for RPM output
HUMIDIFIER_FAN_RPM_PULSE = 2     # Pulses per fan revolution

INTAKE_FAN_RPM_PIN = 22         # Pin for RPM output
INTAKE_FAN_RPM_PULSE = 2        # Pulses per fan revolution

EXHAUST_FAN_RPM_PIN = 6         # Pin for RPM output
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

MIN_CO2_CONTENT = 500
TARGET_CO2_CONTENT = 600        # [Parts per Million CO2]
MAX_CO2_CONTENT = 700
CO2_TOLERANCE_BAND = 0.10

FAN_MIN = 0
FAN_LOW = 25
FAN_MID = 50
FAN_HIGH = 75
FAN_MAX = 100

FAN_MAX_SPEED = 1600            # [RPM]
FAN_EFFICIENCY = 0.95           # [%]

def trim_samples(sample_id):
    if sample_id > 25920:
        present_first_sample = DataLog.query.first()
        historical_sample = DataLogHistorical(present_first_sample)
        db.session.add(historical_sample)
        db.session.delete(present_first_sample)
        db.session.commit()

def set_fan_speed(target_fan, fan_speed):
    target_fan.ChangeDutyCycle(fan_speed)
    return

def read_fan_speed(fan, pulse):
    global initial_time

    dt = time.time() - initial_time
    if dt < 0.005:
        return

    frequency = 1 / dt
    rpm = (frequency / pulse) * 60
    print(f'{fan} FAN SPEED = {rpm} RPM')

def read_fan_speed_alt(fan, duty_cycle):
    fan_speed_approx = FAN_MAX_SPEED * FAN_EFFICIENCY * duty_cycle
    return fan_speed_approx

def fan_control(temperature, humidity, carbon_dioxide):    
    # Temperature Control
    if temperature >= MAX_TEMPERATURE:
        set_fan_speed(intake_fan, FAN_MAX)
        print(f'TEMPERATURE READING OF {temperature}°F - SETTING INTAKE FAN TO {FAN_MAX}%')
    elif temperature >= TARGET_TEMPERATURE * (1 + TEMPERATURE_TOLERANCE_BAND) and temperature < MAX_TEMPERATURE:
        set_fan_speed(intake_fan, FAN_HIGH)
        print(f'TEMPERATURE READING OF {temperature}°F - SETTING INTAKE FAN TO {FAN_HIGH}%')
    elif temperature <= TARGET_TEMPERATURE * (1 - TEMPERATURE_TOLERANCE_BAND) and temperature > MIN_TEMPERATURE:
        set_fan_speed(intake_fan, FAN_MID)
        print(f'TEMPERATURE READING OF {temperature}°F - SETTING INTAKE FAN TO {FAN_MID}%')
    elif temperature <= MIN_TEMPERATURE:
        set_fan_speed(intake_fan, FAN_LOW)
        print(f'TEMPERATURE READING OF {temperature}°F - SETTING INTAKE FAN TO {FAN_LOW}%')
    else:
        set_fan_speed(intake_fan, FAN_MID)
        print(f'TEMPERATURE READING OF {temperature}°F - SETTING INTAKE FAN TO {FAN_MID}%')

    # Humidity Control
    if humidity <= MIN_HUMIDITY:
        set_fan_speed(humidifer_fan, FAN_MAX)
        # Power on humidifier disc
        print(f'HUMIDITY READING OF {humidity}% - POWERING ON HUMIDIFIER AND SETTING FAN TO {FAN_MAX}%')
    elif humidity <= TARGET_HUMIDITY * (1 - HUMIDITY_TOLERANCE_BAND) and humidity > MIN_HUMIDITY:
        set_fan_speed(humidifer_fan, FAN_HIGH)
        # Power on humidifier disc
        print(f'HUMIDITY READING OF {humidity}% - POWERING ON HUMIDIFIER AND SETTING FAN TO {FAN_HIGH}%')
    elif humidity <= TARGET_HUMIDITY * (1 + HUMIDITY_TOLERANCE_BAND) and humidity > TARGET_HUMIDITY * (1 - HUMIDITY_TOLERANCE_BAND):
        set_fan_speed(humidifer_fan, FAN_MID)
        # Power on humidifier disc
        print(f'HUMIDITY READING OF {humidity}% - POWERING ON HUMIDIFIER AND SETTING FAN TO {FAN_MID}%')
    elif humidity <= MAX_HUMIDITY and humidity > TARGET_HUMIDITY * (1 + HUMIDITY_TOLERANCE_BAND):
        set_fan_speed(humidifer_fan, FAN_LOW)
        # Power off humidifier disc
        print(f'HUMIDITY READING OF {humidity}% - POWERING OFF HUMIDIFIER AND SETTING FAN TO {FAN_LOW}%')
    else:
        set_fan_speed(humidifer_fan, FAN_LOW)
        # Power off humidifier disc
        print(f'HUMIDITY READING OF {humidity}% - POWERING OFF HUMIDIFIER AND SETTING FAN TO {FAN_MIN}%')

    # Carbon Dioxide Content Control
    if carbon_dioxide >= MAX_CO2_CONTENT:
        set_fan_speed(exhaust_fan, FAN_MAX)
        print(f'CARBON DIOXIDE READING OF {carbon_dioxide} PPM - SETTING EXHAUST FAN SPEED TO {FAN_MAX}%')
    elif carbon_dioxide >= TARGET_CO2_CONTENT * (1 + CO2_TOLERANCE_BAND) and carbon_dioxide < MAX_CO2_CONTENT:
        set_fan_speed(exhaust_fan, FAN_HIGH)
        print(f'CARBON DIOXIDE READING OF {carbon_dioxide} PPM - SETTING EXHAUST FAN SPEED TO {FAN_HIGH}%')
    elif carbon_dioxide <= TARGET_CO2_CONTENT * (1 - CO2_TOLERANCE_BAND) and carbon_dioxide > MIN_CO2_CONTENT:
        set_fan_speed(exhaust_fan, FAN_MID)
        print(f'CARBON DIOXIDE READING OF {carbon_dioxide} PPM - SETTING EXHAUST FAN SPEED TO {FAN_MID}%')
    elif carbon_dioxide <= MIN_CO2_CONTENT:
        set_fan_speed(exhaust_fan, FAN_LOW)
        print(f'CARBON DIOXIDE READING OF {carbon_dioxide} PPM - SETTING EXHAUST FAN SPEED TO {FAN_LOW}%')
    else:
        set_fan_speed(exhaust_fan, FAN_MID)
        print(f'CARBON DIOXIDE READING OF {carbon_dioxide} PPM - SETTING EXHAUST FAN SPEED TO {FAN_MID}%')

try:
    print('Initializing control...')
    # Initialize PWM fan control
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(HUMIDIFIER_FAN_PWM_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(INTAKE_FAN_PWM_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(EXHAUST_FAN_PWM_PIN, GPIO.OUT, initial=GPIO.LOW)

    GPIO.setup(HUMIDIFIER_FAN_RPM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(INTAKE_FAN_RPM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(EXHAUST_FAN_RPM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    humidifer_fan = GPIO.PWM(HUMIDIFIER_FAN_PWM_PIN, HUMIDIFIER_FAN_PWM_FREQ)
    intake_fan = GPIO.PWM(INTAKE_FAN_PWM_PIN, INTAKE_FAN_PWM_FREQ)
    exhaust_fan = GPIO.PWM(EXHAUST_FAN_PWM_PIN, EXHAUST_FAN_PWM_FREQ)

    humidifer_fan.start(FAN_MIN)
    intake_fan.start(FAN_MIN)
    exhaust_fan.start(FAN_MIN)

    # Fan RPM data collection
    # GPIO.add_event_detect(HUMIDIFIER_FAN_RPM_PIN, GPIO.FALLING)
    # GPIO.add_event_detect(INTAKE_FAN_RPM_PIN, GPIO.FALLING)
    # GPIO.add_event_detect(EXHAUST_FAN_RPM_PIN, GPIO.FALLING)

    # Runtime
    while True:
        try:
            # Retrieve current latest sample number from database
            try:
                sample_num = DataLog.query.order_by(DataLog.id.desc()).first().id
            except AttributeError as error:
                sample_num = 0
            sample_num += 1

            # Collect data points from DHT22 and MH-Z19B sensors
            current_time = datetime.datetime.now()
            temperature = round(dht_device.temperature * (9 / 5) + 32, 2)
            humidity = dht_device.humidity
            # carbon_dioxide = mh_z19.read()['co2']
            carbon_dioxide = mh_z19.read_from_pwm(gpio=12, range=4000)['co2']
            print(f'Sample Number: {sample_num} | Time of Sample: {current_time} | Temperature: {temperature} | Humidity: {humidity} | Carbon Dioxide: {carbon_dioxide}')

            sample = DataLog(id=sample_num, time=current_time, temperature=temperature, humidity=humidity, carbon_dioxide=carbon_dioxide)
            db.session.add(sample)
            db.session.commit()

            trim_samples(sample_num)

            # Controller
            fan_control(temperature, humidity, carbon_dioxide)
            
            time.sleep(sampling_frequency / 2)

            initial_time = time.time()
            GPIO.add_event_detect(HUMIDIFIER_FAN_RPM_PIN, GPIO.FALLING, callback=lambda x: read_fan_speed('Humidifier', HUMIDIFIER_FAN_RPM_PULSE))
            GPIO.add_event_detect(INTAKE_FAN_RPM_PIN, GPIO.FALLING, callback=lambda x: read_fan_speed('Intake', INTAKE_FAN_RPM_PULSE))
            GPIO.add_event_detect(EXHAUST_FAN_RPM_PIN, GPIO.FALLING, callback=lambda x: read_fan_speed('Exhaust', EXHAUST_FAN_RPM_PULSE))

            GPIO.remove_event_detect(HUMIDIFIER_FAN_RPM_PIN)
            GPIO.remove_event_detect(INTAKE_FAN_RPM_PIN)
            GPIO.remove_event_detect(EXHAUST_FAN_RPM_PIN)

            # Tachometer
            # if GPIO.event_detected(HUMIDIFIER_FAN_RPM_PIN):
            #     read_fan_speed('Humidifier', HUMIDIFIER_FAN_RPM_PULSE)
            # if GPIO.event_detected(INTAKE_FAN_RPM_PIN):
            #     read_fan_speed('Intake', INTAKE_FAN_RPM_PULSE)
            # if GPIO.event_detected(EXHAUST_FAN_RPM_PIN):
            #     read_fan_speed('Exhaust', EXHAUST_FAN_RPM_PULSE)

            time.sleep(sampling_frequency / 2)

        except RuntimeError as error:
            print(error.args[0])
            time.sleep(sampling_frequency)
            continue

        except Exception as error:
            dht_device.exit()
            raise error

except KeyboardInterrupt:
    print(f'''
        CANCELLED CONTROL:
        SETTING HUMIDIFIER FAN SPEED TO {FAN_HIGH}%
        SETTING INTAKE FAN SPEED TO {FAN_HIGH}%
        SETTING EXHAUST FAN SPEED TO {FAN_HIGH}%
    ''')
    set_fan_speed(humidifer_fan, FAN_HIGH)
    set_fan_speed(intake_fan, FAN_HIGH)
    set_fan_speed(exhaust_fan, FAN_HIGH)
    GPIO.cleanup()