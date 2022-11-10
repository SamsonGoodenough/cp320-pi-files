import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

GPIO_SERVO = 18
GPIO_TRIGGER = 19
GPIO_ECHO = 26

LEFT = 0.5/20.0 * 100 # by testing (0.5ms)
RIGHT = 2.5/20.0 * 100 # by testing (2.5ms)
MIDDLE = 1.5/20.0 * 100  # by calculation (1.5ms / 20ms * 100)
DEG = (RIGHT - LEFT) / 190.0 # assume range of server is ~190deg

GPIO.setup(GPIO_SERVO, GPIO.OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

p = GPIO.PWM(18, 50)  # channel=18 frequency=50Hz
p.start(MIDDLE)
time.sleep(1)

def distance():
  # set Trigger to HIGH
  GPIO.output(GPIO_TRIGGER, True)

  # set Trigger after 0.01ms to LOW
  time.sleep(0.00001)
  GPIO.output(GPIO_TRIGGER, False)

  StartTime = time.time()
  StopTime = time.time()

  # save StartTime
  while GPIO.input(GPIO_ECHO) == 0:
      StartTime = time.time()

  # save time of arrival
  while GPIO.input(GPIO_ECHO) == 1:
      StopTime = time.time()

  # time difference between start and arrival
  TimeElapsed = StopTime - StartTime
  # multiply with the sonic speed (34300 cm/s)
  # and divide by 2, because there and back
  distance = (TimeElapsed * 34300) / 2

  return distance

def mapToAngle(value, minD, maxD, minA, maxA):
  output = minA + (float(value - minD) / float(maxD - minD) * (maxA - minA))
  return max(min(output, maxA), minA)

if __name__ == '__main__':
  try:
    while True:
      dist = distance()
      degrees = mapToAngle(dist, 0, 30, 0, 190)
      angle = LEFT + DEG*degrees
      p.ChangeDutyCycle(angle)
      print ("Measured Distance = %.1f cm" % dist)
      print ("Changing Angle = %.1f deg" % degrees)
      time.sleep(0.7)

  # Reset by pressing CTRL + C
  except KeyboardInterrupt:
    print("\nMeasurement stopped by User")
    time.sleep(1)
    p.ChangeDutyCycle(MIDDLE)
    time.sleep(1)
    p.stop()
    GPIO.cleanup()