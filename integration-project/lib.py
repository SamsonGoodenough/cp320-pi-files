import time
import smbus
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

class LED_Manager:
  # CLASS CONSTANTS
  DEFAULT_DUTY = 50
  DEFAULT_FREQ = 50
  DEFAULT_LED_RED_GPIO = 21
  DEFAULT_LED_GREEN_GPIO = 20
  DEFAULT_LED_BLUE_GPIO = 16
  
  MIN_MAP = 0
  MIN_RED = 20
  MIN_GREEN = 20
  MIN_BLUE = 80
  MAX_MAP_BLUE = 230
  MAX_MAP = 255
  
  MIN_DUTY = 0
  MAX_DUTY = 100
  MAX_DUTY_BLUE = 8
  
  HALF = 0.5
  
  def __init__(self, red_gpio=DEFAULT_LED_RED_GPIO, green_gpio=DEFAULT_LED_GREEN_GPIO,
               blue_gpio=DEFAULT_LED_BLUE_GPIO):
    GPIO.setup(red_gpio, GPIO.OUT)
    GPIO.setup(green_gpio, GPIO.OUT)
    GPIO.setup(blue_gpio, GPIO.OUT)
    
    self.red_led = GPIO.PWM(red_gpio, LED_Manager.DEFAULT_FREQ)
    self.green_led = GPIO.PWM(green_gpio, LED_Manager.DEFAULT_FREQ)
    self.blue_led = GPIO.PWM(blue_gpio, LED_Manager.DEFAULT_FREQ)
    self.enabled = True
    self.inversed = False
    self.start_LEDs()
  
  def start_LEDs(self):
    self.red_led.start(LED_Manager.DEFAULT_DUTY)
    self.green_led.start(LED_Manager.DEFAULT_DUTY)
    self.blue_led.start(LED_Manager.DEFAULT_DUTY)
    time.sleep(1) # give time to start
  
  def update_LEDs(self, red, green, blue):
    red = Helper.map(abs(LED_Manager.MAX_MAP-red), LED_Manager.MIN_RED, LED_Manager.MAX_MAP, LED_Manager.MIN_DUTY, LED_Manager.MAX_DUTY)
    green = Helper.map(abs(green-(LED_Manager.MAX_MAP*LED_Manager.HALF)), LED_Manager.MIN_GREEN, LED_Manager.MAX_MAP, LED_Manager.MIN_DUTY, LED_Manager.MAX_DUTY)
    blue = Helper.map(abs(LED_Manager.MIN_MAP-blue), LED_Manager.MIN_BLUE, LED_Manager.MAX_MAP_BLUE, LED_Manager.MIN_DUTY, LED_Manager.MAX_DUTY_BLUE)
    
    if self.enabled:
      if self.inversed:
        self.red_led.ChangeDutyCycle(abs(blue))
        self.green_led.ChangeDutyCycle(abs(green))
        self.blue_led.ChangeDutyCycle(abs(red))
      else:
        self.red_led.ChangeDutyCycle(abs(red))
        self.green_led.ChangeDutyCycle(abs(green))
        self.blue_led.ChangeDutyCycle(abs(blue))
        
  def off_LEDs(self):
    self.red_led.ChangeDutyCycle(LED_Manager.MIN_DUTY)
    self.green_led.ChangeDutyCycle(abs(LED_Manager.MIN_DUTY))
    self.blue_led.ChangeDutyCycle(abs(LED_Manager.MIN_DUTY))
        
  def on_LEDs(self):
    self.red_led.ChangeDutyCycle(LED_Manager.DEFAULT_DUTY)
    self.green_led.ChangeDutyCycle(abs(LED_Manager.DEFAULT_DUTY))
    self.blue_led.ChangeDutyCycle(abs(LED_Manager.DEFAULT_DUTY))
    
  def stop(self):
    self.red_led.stop()
    self.green_led.stop()
    self.blue_led.stop()
  

class Photo_Manager:
  # CLASS CONSTANTS
  DEFAULT_ADDRESS = 0x48
  DEFAULT_PHOTO_ADDRESS = 0x40
  
  MIN_VALUE = 0
  MAX_VALUE = 255
  
  def __init__(self, address=DEFAULT_ADDRESS, photo_address=DEFAULT_PHOTO_ADDRESS):
    self.address = address
    self.photo_address = photo_address
    self.photo_bus = smbus.SMBus(1)
  
  def getValue(self):
    self.photo_bus.write_byte(self.address, self.photo_address)
    return self.photo_bus.read_byte(self.address)


class UltraSonic_Manager:
  # CLASS CONSTANTS
  GPIO_TRIGGER = 19
  GPIO_ECHO = 26
  
  LEFT = 0.5/20.0 * 100 # by testing (0.5ms)
  RIGHT = 2.5/20.0 * 100 # by testing (2.5ms)
  MIDDLE = 1.5/20.0 * 100  # by calculation (1.5ms / 20ms * 100)
  DEG = (RIGHT - LEFT) / 190.0 # assume range of server is ~190deg
  
  DISTANCE_SLEEP = 0.00001
  SPEED_OF_SOUND = 34300 # cm/s
  HALF = 0.5
  
  MIN_DISTANCE = 0
  MAX_DISTANCE = 100
  
  def __init__(self):
    GPIO.setup(UltraSonic_Manager.GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(UltraSonic_Manager.GPIO_ECHO, GPIO.IN)
    self.max_distance = UltraSonic_Manager.MAX_DISTANCE
    self.enabled = True
  
  def getDistance(self):
    if self.enabled:
      GPIO.output(UltraSonic_Manager.GPIO_TRIGGER, True)
      time.sleep(UltraSonic_Manager.DISTANCE_SLEEP)
      GPIO.output(UltraSonic_Manager.GPIO_TRIGGER, False)
      
      start = time.time()
      stop = time.time()
      
      while GPIO.input(UltraSonic_Manager.GPIO_ECHO) == 0:
        start = time.time()
      while GPIO.input(UltraSonic_Manager.GPIO_ECHO) == 1:
        stop = time.time()
        
      elapsed = stop - start
      distance = (elapsed * UltraSonic_Manager.SPEED_OF_SOUND) * UltraSonic_Manager.HALF
    
      return distance
    
    return UltraSonic_Manager.MIN_DISTANCE
  
  def setMaxDistance(self, distance):
    self.max_distance = distance
  
  
class Servo_Manager:
  # CLASS CONSTANTS
  GPIO_PIN = 18
  FREQUENCY = 50
  
  LEFT = 0.5/20.0 * 100 # by testing (0.5ms)
  RIGHT = 2.5/20.0 * 100 # by testing (2.5ms)
  MIDDLE = 1.5/20.0 * 100  # by calculation (1.5ms / 20ms * 100)
  DEG = (RIGHT - LEFT) / 190.0 # assume range of server is ~190deg
  
  MIN_ANGLE = 0
  MAX_ANGLE = 190
  
  SERVO_DELAY = 0.7
  
  def __init__(self):
    GPIO.setup(Servo_Manager.GPIO_PIN, GPIO.OUT)
    self.servo = GPIO.PWM(Servo_Manager.GPIO_PIN, Servo_Manager.FREQUENCY)
    self.servo.start(Servo_Manager.MIDDLE)
    self.enabled = True
  
  def getAngle(self, distance):
    if self.enabled:
      degrees = Helper.mapToAngle(distance, UltraSonic_Manager.MIN_DISTANCE, UltraSonic_Manager.MAX_DISTANCE, Servo_Manager.MIN_ANGLE, Servo_Manager.MAX_ANGLE)
      angle = (UltraSonic_Manager.LEFT + (degrees * UltraSonic_Manager.DEG))
      return angle
    
    return 0
  
  def setAngle(self, angle):
    if self.enabled:
      self.servo.ChangeDutyCycle(angle)
      time.sleep(Servo_Manager.SERVO_DELAY)
  
  def stop(self):
    self.servo.stop()


class Console_Manager:
  MENU_LENGTH = 12
  
  def __init__(self, led_manager, photo_manager, ultra_manager, servo_manager):
    self.led_manager = led_manager
    self.photo_manager = photo_manager
    self.ultra_manager = ultra_manager
    self.servo_manager = servo_manager
  
  def menu(self):
    while True:
      print('='*Console_Manager.MENU_LENGTH, 'MENU', '='*Console_Manager.MENU_LENGTH)
      print('1.\tToggle LEDs')
      print('2.\tInvert LED Direction')
      print('3.\tToggle UltraSonic Sensor')
      print('4.\tToggle Servo')
      print('5.\tRun Program')
      print('6.\tExit')
      
      user_input = input('Enter your choice: ')
      if user_input == '1':
        self.toggleLEDs()
      elif user_input == '2':
        self.invertLEDs()
      elif user_input == '3':
        self.toggleUltraSonic()
      elif user_input == '4':
        self.toggleServo()
      elif user_input == '5':
        print('Running Program...\n\nPress Ctrl+C to return to menu')
        break
      elif user_input == '6':
        print('Exiting...')
        return False
      else:
        print('Invalid input\n')
      print()
    return True

  def toggleLEDs(self):
    self.led_manager.enabled = not self.led_manager.enabled
    if not self.led_manager.enabled:
      self.led_manager.off_LEDs()
    else:
      self.led_manager.on_LEDs()
    print('LEDs are now', 'enabled' if self.led_manager.enabled else 'disabled')
    
  def invertLEDs(self):
    self.led_manager.inversed = not self.led_manager.inversed
    print('LEDs are now', 'inversed' if self.led_manager.inversed else 'not inversed')

  def toggleUltraSonic(self):
    self.ultra_manager.enabled = not self.ultra_manager.enabled
    print('UltraSonic Sensor is now', 'enabled' if self.ultra_manager.enabled else 'disabled')

  def toggleServo(self):
    self.servo_manager.enabled = not self.servo_manager.enabled
    print('Servo is now', 'enabled' if self.servo_manager.enabled else 'disabled')


class Helper:
  SLEEP_LOOP = 0.1
  
  @staticmethod
  def map(value, minA, maxA, minB, maxB):
    output = minB + (float(value - minA) / float(maxA - minA) * (maxB - minB))
    return max(min(output, maxB), minB)
  
  @staticmethod
  def mapToAngle(value, minD, maxD, minA, maxA):
    output = minA + (float(value - minD) / float(maxD - minD) * (maxA - minA))
    return max(min(output, maxA), minA)
  
  def delay():
    time.sleep(Helper.SLEEP_LOOP)
  
  def GPIO_cleanup():
    GPIO.cleanup()