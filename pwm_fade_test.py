import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)

p = GPIO.PWM(18, 60)  # channel=18 frequency=60Hz
p2 = GPIO.PWM(19, 60)  # channel=18 frequency=60Hz
p.start(50)
p2.start(50)
time.sleep(2)
FADE_TIME=10
INCREMENT=1
level=0
try:
    while level <= FADE_TIME:
            print(level)
            p.ChangeDutyCycle(level*10)
            p2.ChangeDutyCycle(100-level*10)
            level += INCREMENT
            time.sleep(INCREMENT)
except KeyboardInterrupt:
    pass
p.stop()
p2.stop()
GPIO.cleanup()
