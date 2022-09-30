import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)

p = GPIO.PWM(18, 60)  # channel=18 frequency=60Hz
p2 = GPIO.PWM(19, 60)  # channel=18 frequency=60Hz
p.start(50)
p2.start(50)
time.sleep(5)
try:
    while True:
            p.ChangeDutyCycle(90)
            p2.ChangeDutyCycle(10)
            time.sleep(5)
            p.ChangeDutyCycle(10)
            p2.ChangeDutyCycle(90)
            time.sleep(5)
except KeyboardInterrupt:
    pass
p.stop()
p2.stop()
GPIO.cleanup()
