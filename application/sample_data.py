from itertools import cycle
import time
import datetime
import board
import adafruit_dht
import mh_z19
import RPi.GPIO as GPIO
import json

from __init__ import db
from models import DataLog

# Initialize runtime parameters
dht_device = adafruit_dht.DHT22(board.D4)
sampling_frequency = 30.0

# Initialization for Humidifier power
HUMIDIFIER_POWER_PIN = 10

# Initialization for PWM control
HUMIDIFIER_FAN_PWM_PIN = 23     # Pin used to control PWM fan
HUMIDIFIER_FAN_PWM_FREQ = 25    # [Hz] Frequency for PWM control

# ****************************************************************
# INTAKE PARAMETERS NOT NECESSARY DUE TO NEGATIVE PRESSURE CONFIGURATION OF GREENHOUSE
# ****************************************************************
INTAKE_FAN_PWM_PIN = 27         # Pin used to control PWM fan
INTAKE_FAN_PWM_FREQ = 25        # [Hz] Frequency for PWM control

EXHAUST_FAN_PWM_PIN = 5         # Pin used to control PWM fan
EXHAUST_FAN_PWM_FREQ = 25       # [Hz] Frequency for PWM control

# Fan speed presets
FAN_MIN = 0
FAN_LOW = 25
FAN_MID = 50
FAN_HIGH = 75
FAN_MAX = 100

def select_species(species_list):
    print('Which species should control parameters be loaded for?')
    for each in species_list:
        print(f'{each} [{species_list.index(each) + 1}]')
    selected_species_code = input('Please select a species by typing in the corresponding number designation: ')
    try:
        if int(selected_species_code) < 1:
            print('Please select a code that is positive and nonzero')
            time.sleep(1.5)
            select_species(species_list)

        selected_species = species_list[int(selected_species_code) - 1]
        print(f'You have selected {selected_species.upper()}')
        time.sleep(2.0)
        print('If the species selection is incorrect, exit the program and make another selection\n')
        time.sleep(5.0)
        return selected_species

    except (TypeError, IndexError) as err:
        print('Restarting program due to error:')
        print(err)
        time.sleep(1.5)
        select_species(species_list)

def load_parameters(parameter_file):
    global TARGET_TEMPERATURE
    global MIN_TEMPERATURE
    global MAX_TEMPERATURE
    global TEMPERATURE_TOLERANCE_BAND

    global TARGET_HUMIDITY
    global MIN_HUMIDITY
    global MAX_HUMIDITY
    global HUMIDITY_TOLERANCE_BAND

    global TARGET_CO2_CONTENT
    global MIN_CO2_CONTENT
    global MAX_CO2_CONTENT
    global CO2_TOLERANCE_BAND

    time.sleep(1.0)
    i = 0
    for parameter in parameter_file[species_choice][control_mode]:
        if i == 0:
            TARGET_TEMPERATURE = parameter_file[species_choice][control_mode][parameter].get("Target")
            MIN_TEMPERATURE = parameter_file[species_choice][control_mode][parameter].get("Minimum")
            MAX_TEMPERATURE = parameter_file[species_choice][control_mode][parameter].get("Maximum")
            TEMPERATURE_TOLERANCE_BAND = parameter_file[species_choice][control_mode][parameter].get("Tolerance")
        elif i == 1:
            TARGET_HUMIDITY = parameter_file[species_choice][control_mode][parameter].get("Target")
            MIN_HUMIDITY = parameter_file[species_choice][control_mode][parameter].get("Minimum")
            MAX_HUMIDITY = parameter_file[species_choice][control_mode][parameter].get("Maximum")
            HUMIDITY_TOLERANCE_BAND = parameter_file[species_choice][control_mode][parameter].get("Tolerance")
        elif i == 2:
            TARGET_CO2_CONTENT = parameter_file[species_choice][control_mode][parameter].get("Target")
            MIN_CO2_CONTENT = parameter_file[species_choice][control_mode][parameter].get("Minimum")
            MAX_CO2_CONTENT = parameter_file[species_choice][control_mode][parameter].get("Maximum")
            CO2_TOLERANCE_BAND = parameter_file[species_choice][control_mode][parameter].get("Tolerance")
        
        print(f'''{parameter.upper()}:
TARGET = {parameter_file[species_choice][control_mode][parameter].get("Target")}
MINIMUM = {parameter_file[species_choice][control_mode][parameter].get("Minimum")}
MAXIMUM = {parameter_file[species_choice][control_mode][parameter].get("Maximum")}
TOLERANCE = {parameter_file[species_choice][control_mode][parameter].get("Tolerance")}
''')
        i += 1
    time.sleep(5.0)

def set_fan_speed(target_fan, fan_speed):
    target_fan.ChangeDutyCycle(fan_speed)
    return

def cycle_power_humidifier(desired_state):
    try:
        # Checks state of the humidifier power pin. If desired state is ON and pin is currently set to HIGH, then it will cycle to LOW and vice versa
        if GPIO.input(HUMIDIFIER_POWER_PIN) == 1 and desired_state == 'ON':
            GPIO.output(HUMIDIFIER_POWER_PIN, GPIO.LOW)
            print('Humidifier powered ON')

        elif GPIO.input(HUMIDIFIER_POWER_PIN) == 0 and desired_state == 'OFF':
            GPIO.output(HUMIDIFIER_POWER_PIN, GPIO.HIGH)
            time.sleep(1.0)
            GPIO.output(HUMIDIFIER_POWER_PIN, GPIO.LOW)
            time.sleep(1.0)
            GPIO.output(HUMIDIFIER_POWER_PIN, GPIO.HIGH)
            print('Humidifier powered OFF')

        return
    except RuntimeError as error:
        print(error.args[0])
        return

def fan_control(temperature, humidity, carbon_dioxide):
    # Temperature Control
    if temperature >= MAX_TEMPERATURE:
        set_fan_speed(intake_fan, FAN_MAX)
        print(f'TEMP = {temperature}°F => INTAKE TO {FAN_MAX}%')

    elif temperature >= TARGET_TEMPERATURE * (1 + TEMPERATURE_TOLERANCE_BAND) and temperature < MAX_TEMPERATURE:
        set_fan_speed(intake_fan, FAN_HIGH)
        print(f'TEMP = {temperature}°F => INTAKE TO {FAN_HIGH}%')

    elif temperature <= TARGET_TEMPERATURE * (1 - TEMPERATURE_TOLERANCE_BAND) and temperature > MIN_TEMPERATURE:
        set_fan_speed(intake_fan, FAN_MID)
        print(f'TEMP = {temperature}°F => INTAKE TO {FAN_MID}%')

    elif temperature <= MIN_TEMPERATURE:
        set_fan_speed(intake_fan, FAN_LOW)
        print(f'TEMP = {temperature}°F => INTAKE TO {FAN_LOW}%')

    else:
        set_fan_speed(intake_fan, FAN_MID)
        print(f'TEMP = {temperature}°F => INTAKE TO {FAN_MID}%')

    # Humidity Control
    if humidity <= MIN_HUMIDITY:
        set_fan_speed(humidifer_fan, FAN_MAX)
        cycle_power_humidifier('ON')
        print(f'RH% = {humidity}% => HUMIDIFIER ON AND FAN TO {FAN_MAX}%')

    elif humidity <= TARGET_HUMIDITY * (1 - HUMIDITY_TOLERANCE_BAND) and humidity > MIN_HUMIDITY:
        set_fan_speed(humidifer_fan, FAN_HIGH)
        cycle_power_humidifier('ON')
        print(f'RH% = {humidity}% => HUMIDIFIER ON AND FAN TO {FAN_HIGH}%')

    elif humidity <= TARGET_HUMIDITY * (1 + HUMIDITY_TOLERANCE_BAND) and humidity > TARGET_HUMIDITY * (1 - HUMIDITY_TOLERANCE_BAND):
        set_fan_speed(humidifer_fan, FAN_MID)
        cycle_power_humidifier('ON')
        print(f'RH% = {humidity}% => HUMIDIFIER ON AND FAN TO {FAN_MID}%')

    elif humidity <= MAX_HUMIDITY and humidity > TARGET_HUMIDITY * (1 + HUMIDITY_TOLERANCE_BAND):
        set_fan_speed(humidifer_fan, FAN_LOW)
        cycle_power_humidifier('OFF')
        print(f'RH% = {humidity}% => HUMIDIFIER OFF AND FAN TO {FAN_LOW}%')

    else:
        set_fan_speed(humidifer_fan, FAN_LOW)
        cycle_power_humidifier('OFF')
        print(f'RH% = {humidity}% => HUMIDIFIER OFF AND FAN TO {FAN_MIN}%')

    # Carbon Dioxide Content Control
    if carbon_dioxide >= MAX_CO2_CONTENT:
        set_fan_speed(exhaust_fan, FAN_MAX)
        print(f'CO2 = {carbon_dioxide} PPM => EXHAUST TO {FAN_MAX}%')

    elif carbon_dioxide >= TARGET_CO2_CONTENT * (1 + CO2_TOLERANCE_BAND) and carbon_dioxide < MAX_CO2_CONTENT:
        set_fan_speed(exhaust_fan, FAN_MID)
        print(f'CO2 = {carbon_dioxide} PPM => EXHAUST TO {FAN_MID}%')

    elif carbon_dioxide <= TARGET_CO2_CONTENT * (1 - CO2_TOLERANCE_BAND) and carbon_dioxide > MIN_CO2_CONTENT:
        set_fan_speed(exhaust_fan, FAN_LOW)
        print(f'CO2 = {carbon_dioxide} PPM => EXHAUST TO {FAN_LOW}%')
        
    elif carbon_dioxide <= MIN_CO2_CONTENT:
        set_fan_speed(exhaust_fan, FAN_MIN)
        print(f'CO2 = {carbon_dioxide} PPM => EXHAUST TO {FAN_MIN}%')
        
    else:
        set_fan_speed(exhaust_fan, FAN_MIN)
        print(f'CO2 = {carbon_dioxide} PPM => EXHAUST TO {FAN_MIN}%')

try:
    # Load mushroom control parameters for desired species
    params_file = json.loads(open('mushroom-params.json').read())
    species_list = []
    for species in params_file:
        species_list.append(species)
    species_choice = select_species(species_list)

    # Load parameters for the selected species
    control_mode = 'Fruiting'
    print(f'Loading control parameters for {control_mode.upper()}...')
    load_parameters(params_file)

    print('Initializing control...')
    # Initialize PWM fan control
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # Initialize humidifier power
    GPIO.setup(HUMIDIFIER_POWER_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.output(HUMIDIFIER_POWER_PIN, GPIO.HIGH)

    # Initialize all fans
    GPIO.setup(HUMIDIFIER_FAN_PWM_PIN, GPIO.OUT, initial=GPIO.LOW)
    humidifer_fan = GPIO.PWM(HUMIDIFIER_FAN_PWM_PIN, HUMIDIFIER_FAN_PWM_FREQ)
    humidifer_fan.start(FAN_MIN)

    GPIO.setup(INTAKE_FAN_PWM_PIN, GPIO.OUT, initial=GPIO.LOW)
    intake_fan = GPIO.PWM(INTAKE_FAN_PWM_PIN, INTAKE_FAN_PWM_FREQ)
    intake_fan.start(FAN_MIN)

    GPIO.setup(EXHAUST_FAN_PWM_PIN, GPIO.OUT, initial=GPIO.LOW)
    exhaust_fan = GPIO.PWM(EXHAUST_FAN_PWM_PIN, EXHAUST_FAN_PWM_FREQ)
    exhaust_fan.start(FAN_MIN)

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
            carbon_dioxide = mh_z19.read_from_pwm(gpio=12, range=5000)['co2']
            print(f'Sample: {sample_num} | Time: {current_time} | Temperature: {temperature} | Humidity: {humidity} | Carbon Dioxide: {carbon_dioxide}')

            sample = DataLog(id=sample_num, time=current_time, temperature=temperature, humidity=humidity, carbon_dioxide=carbon_dioxide)
            db.session.add(sample)
            db.session.commit()

            # Controller
            fan_control(temperature, humidity, carbon_dioxide)

            time.sleep(sampling_frequency)

        except RuntimeError as error:
            print(error.args[0])
            time.sleep(5)
            continue

        except Exception as error:
            dht_device.exit()
            raise error

except KeyboardInterrupt:
    GPIO.output(HUMIDIFIER_POWER_PIN, GPIO.HIGH)
    time.sleep(2.5)
    GPIO.output(HUMIDIFIER_POWER_PIN, GPIO.LOW)
    set_fan_speed(humidifer_fan, FAN_HIGH)
    set_fan_speed(intake_fan, FAN_HIGH)
    set_fan_speed(exhaust_fan, FAN_HIGH)
    print(f'''
CANCELLED CONTROL:
HUMIDIFIER OFF
HUMIDIFIER FAN TO {FAN_HIGH}%
EXHAUST FAN TO {FAN_HIGH}%
''')
    GPIO.cleanup()