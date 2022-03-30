import time
import RPi.GPIO as GPIO

GPIO_PIN = 10

try:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PIN, GPIO.OUT, initial=GPIO.HIGH)

    while True:
        try:
            print('Turning button ON...')
            GPIO.output(GPIO_PIN, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(GPIO_PIN, GPIO.HIGH)
            time.sleep(2.5)
            print('Turning button OFF...')
            GPIO.output(GPIO_PIN, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(GPIO_PIN, GPIO.HIGH)
            time.sleep(2.5)
        except RuntimeError as error:
            print(error.args[0])
except KeyboardInterrupt:
    GPIO.cleanup()