import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)


try: 
	while True:
		GPIO.output(18,False)
		time.sleep(1)
		GPIO.output(18,True)
		time.sleep(1)
except KeyboardInterrupt:
	pass

finally:
	GPIO.cleanup()

