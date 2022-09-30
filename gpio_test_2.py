import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)


try: 
	while True:
		GPIO.output(12,False)
		time.sleep(1)
		GPIO.output(12,True)
		time.sleep(1)
except KeyboardInterrupt:
	pass

finally:
	GPIO.cleanup()

