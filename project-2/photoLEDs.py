import time
import smbus
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

LED_RED_GPIO = 21
LED_GREEN_GPIO = 20
LED_BLUE_GPIO = 16

ADDRESS = 0x48
PHOTO_ADDRESS = 0x40 # Photoresistor | Range from 3 - 0.2

GPIO.setup(LED_RED_GPIO, GPIO.OUT)
GPIO.setup(LED_GREEN_GPIO, GPIO.OUT)
GPIO.setup(LED_BLUE_GPIO, GPIO.OUT)

red = GPIO.PWM(LED_RED_GPIO, 60)  # frequency=60Hz
green = GPIO.PWM(LED_GREEN_GPIO, 60)  # frequency=60Hz
blue = GPIO.PWM(LED_BLUE_GPIO, 60)  # frequency=60Hz
bus = smbus.SMBus(1)

red.start(50)
green.start(50)
blue.start(50)
time.sleep(1)

def map(value, minA, maxA, minB, maxB):
  output = minB + (float(value - minA) / float(maxA - minA) * (maxB - minB))
  return max(min(output, maxB), minB)

try:
  while True:
    bus.write_byte(ADDRESS,PHOTO_ADDRESS)
    value = bus.read_byte(ADDRESS)
    print(value)
    
    red.ChangeDutyCycle(map(abs(255-value), 20, 255, 0, 100))
    green.ChangeDutyCycle(map(abs(value-128), 20, 255, 0, 100))
    blue.ChangeDutyCycle(map(abs(0-value), 80, 230, 0, 8))
    
    time.sleep(0.1)
except KeyboardInterrupt:
  pass
  
red.stop()
green.stop()
blue.stop()
GPIO.cleanup()