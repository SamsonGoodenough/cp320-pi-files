import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

p = GPIO.PWM(18, 60)  # channel=18 frequency=60Hz
p.start(50)
time.sleep(5)
try:
    while True:
            p.ChangeDutyCycle(10)
            time.sleep(5)
            p.ChangeDutyCycle(100)
            time.sleep(5)
except KeyboardInterrupt:
    pass
p.stop()
GPIO.cleanup()
