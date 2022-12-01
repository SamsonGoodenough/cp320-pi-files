import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

GPIO_PIR = 16

GPIO.setup(GPIO_PIR, GPIO.IN)

try:
  while True:
    print("Waiting for motion...")
    while GPIO.input(GPIO_PIR) == 0:
      startTime = time.time()
    
    print("Motion detected!")
    while GPIO.input(GPIO_PIR) == 1:
      stopTime = time.time()
      
    motionTime = stopTime - startTime
    print("Motion lasted: %.2f seconds\n" % motionTime)
except KeyboardInterrupt:
  print("\nBye")
  GPIO.cleanup()