import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

LEFT = 0.5/20.0 * 100 # by testing (0.5ms)
RIGHT = 2.5/20.0 * 100 # by testing (2.5ms)
MIDDLE = 1.5/20.0 * 100  # by calculation (1.5ms / 20ms * 100)
DEG = (RIGHT - LEFT) / 190.0 # assume range of server is ~190deg

p = GPIO.PWM(18, 50)  # channel=18 frequency=50Hz
p.start(MIDDLE)
time.sleep(1)
try:
  while True:
    print("What angle do you want the servo?")
    degrees = int(input())
    angle = LEFT + DEG*degrees
    p.ChangeDutyCycle(angle)
    time.sleep(1)
except KeyboardInterrupt:
  pass

time.sleep(1)
p.ChangeDutyCycle(MIDDLE)
time.sleep(1)
p.stop()
GPIO.cleanup()
