import time
import board
import adafruit_dht
import RPi.GPIO as GPIO

FAN1_PIN = 23
FAN1_FREQ = 25
FAN1_RPM = 24
FAN1_PULSE = 2

FAN2_PIN = 27
FAN2_FREQ = 25
FAN2_RPM = 22
FAN2_PULSE = 2

FAN3_PIN = 5
FAN3_FREQ = 25
FAN3_RPM = 6
FAN3_PULSE = 2

def set_fan_speed(target_fan, fan_speed):
    target_fan.ChangeDutyCycle(fan_speed)
    return

def read_fan_speed(fan, pulse):
    dt = time.time() - initial_time
    if dt < 0.005:
        return

    frequency = 1 / dt
    rpm = (frequency / pulse) * 60
    print(f'{fan} fan speed = {rpm} RPM')
    initial_time = time.time()

try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FAN1_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(FAN2_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(FAN3_PIN, GPIO.OUT, initial=GPIO.LOW)

    GPIO.setup(FAN1_RPM, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(FAN2_RPM, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(FAN3_RPM, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    fan1 = GPIO.PWM(FAN1_PIN, FAN1_FREQ)
    fan2 = GPIO.PWM(FAN2_PIN, FAN2_FREQ)
    fan3 = GPIO.PWM(FAN3_PIN, FAN3_FREQ)

    fan1.start(0)
    fan2.start(0)
    fan3.start(0)

    initial_time = time.time()
    GPIO.add_event_detect(FAN1_RPM, GPIO.BOTH)
    GPIO.add_event_detect(FAN2_RPM, GPIO.BOTH)
    GPIO.add_event_detect(FAN3_RPM, GPIO.BOTH)

    duty_cycle = 0
    while True:
        if duty_cycle >= 90:
            set_fan_speed(fan1, 100)
            set_fan_speed(fan2, 100)
            set_fan_speed(fan3, 100)
            print('FAN SPEED SET TO 100')
            time.sleep(10)
            duty_cycle = 0

        set_fan_speed(fan1, duty_cycle)
        set_fan_speed(fan2, duty_cycle)
        set_fan_speed(fan3, duty_cycle)
        print(f'FAN SPEED SET TO {duty_cycle}')
        time.sleep(10)

        initial_time = time.time()
        if GPIO.event_detected(FAN1_RPM):
            read_fan_speed('Humidifier', FAN1_PULSE)

        if GPIO.event_detected(FAN2_RPM):
            read_fan_speed('Intake', FAN2_PULSE)

        if GPIO.event_detected(FAN3_RPM):
            read_fan_speed('Exhaust', FAN3_PULSE)
        
        duty_cycle += 10

except KeyboardInterrupt:
    print(f'''
        CANCELLED CONTROL:
        SETTING HUMIDIFIER FAN SPEED TO {0}%
        SETTING INTAKE FAN SPEED TO {0}%
        SETTING EXHAUST FAN SPEED TO {0}%
    ''')
    set_fan_speed(fan1, 0)
    set_fan_speed(fan2, 0)
    set_fan_speed(fan3, 0)
    GPIO.cleanup()