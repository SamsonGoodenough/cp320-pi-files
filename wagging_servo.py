import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

THEORETICAL_LEFT = 1.0/20.0 * 100 # by calculation (1ms / 20ms * 100)
THEORETICAL_RIGHT = 2.0/20.0 * 100 # by calculation (2ms / 20ms * 100)
LEFT = 0.5/20.0 * 100 # by testing (0.5ms)
RIGHT = 2.5/20.0 * 100 # by testing (2.5ms)
MIDDLE = 1.5/20.0 * 100
p = GPIO.PWM(18, 50)  # channel=18 frequency=50Hz
p.start(MIDDLE)
time.sleep(1)
try:
    while True:
            p.ChangeDutyCycle(LEFT)
            time.sleep(1)
            p.ChangeDutyCycle(RIGHT)
            time.sleep(1)
except KeyboardInterrupt:
    pass

time.sleep(1)
p.ChangeDutyCycle(MIDDLE)
time.sleep(1)
p.stop()
GPIO.cleanup()
