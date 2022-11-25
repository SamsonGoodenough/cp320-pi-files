from lib import LED_Manager, Photo_Manager, UltraSonic_Manager, Servo_Manager, Console_Manager, Helper

led_manager = LED_Manager()
photo_manager = Photo_Manager()
ultrasonic_manager = UltraSonic_Manager()
servo_manager = Servo_Manager()
console_manager = Console_Manager(led_manager, photo_manager, ultrasonic_manager, servo_manager)

try:
  while console_manager.menu():
    try:
      while True:
        photo_value = photo_manager.getValue()
        led_manager.update_LEDs(photo_value, photo_value, photo_value)
        
        # update maximum ultrasonic distance
        ultrasonic_manager.setMaxDistance(Helper.map(Photo_Manager.MAX_VALUE-photo_value, Photo_Manager.MIN_VALUE, Photo_Manager.MAX_VALUE, UltraSonic_Manager.MIN_DISTANCE, UltraSonic_Manager.MAX_DISTANCE))
        
        distance = ultrasonic_manager.getDistance()
        angle = servo_manager.getAngle(distance)
        servo_manager.setAngle(angle)
        
        Helper.delay()
    except KeyboardInterrupt:
      print()
      pass
except Exception as e:
  print(e)
  pass

led_manager.stop()
servo_manager.stop()
Helper.GPIO_cleanup()