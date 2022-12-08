import os
import logging
from dotenv import load_dotenv
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BCM)

GPIO_PIR = 16
GPIO_SERVO = 18
GPIO.setup(GPIO_PIR, GPIO.IN)
GPIO.setup(GPIO_SERVO, GPIO.OUT)

LEFT = 0.5/20.0 * 100 # by testing (0.5ms)
RIGHT = 2.5/20.0 * 100 # by testing (2.5ms)
MIDDLE = 1.5/20.0 * 100
FREQ = 50
servo = GPIO.PWM(GPIO_SERVO, FREQ)  # channel=18 frequency=50Hz
servo.start(MIDDLE)

# enable logging
logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
listen_to_motion = False
alarm_armed = False
alerts = True

SETTINGS_KEYBOARD = [
    [
      InlineKeyboardButton("Arm", callback_data='arm'),
      InlineKeyboardButton("Watch", callback_data='watch'),
    ],
    [InlineKeyboardButton("Done", callback_data='done')],
  ]

# bot functions
def start(update: Update, context: CallbackContext) -> None:
  user = update.effective_user
  update.message.reply_markdown_v2(fr'Hi {user.mention_markdown_v2()}\!')
  update.message.reply_text('Use /help to get a list of commands')
  
def arm(update: Update, context: CallbackContext) -> None:
  global alarm_armed
  alarm_armed = not alarm_armed
  update.message.reply_text('Alarm has been: ' + ('armed' if alarm_armed else 'disarmed'))
  
def watch(update: Update, context: CallbackContext) -> None:
  global listen_to_motion
  global alerts
  listen_to_motion = not listen_to_motion
  alerts = not alerts
  update.message.reply_text('Watching for motion: ' + str(listen_to_motion))

def help_command(update: Update, context: CallbackContext) -> None:
  update.message.reply_text('''/start - Start the bot
/arm - Arm/disarm the alarm (default: disarmed)
/watch - Toggle live watching for motion
/help - Get a list of commands
/commands - Get commands menu''')

def echo(update: Update, context: CallbackContext) -> None:
  update.message.reply_text(update.message.text)

def commands(update: Update, context: CallbackContext) -> None:
  reply_markup = InlineKeyboardMarkup(SETTINGS_KEYBOARD)
  update.message.reply_text('Please choose:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
  """Parses the CallbackQuery and updates the message text."""
  query = update.callback_query

  # CallbackQueries need to be answered, even if no notification to the user is needed
  # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
  query.answer()

  reply_markup = InlineKeyboardMarkup(SETTINGS_KEYBOARD)
  
  if query.data == 'done':
    query.edit_message_text(text="Settings Applied!")
  elif query.data == 'arm':
    global alarm_armed
    alarm_armed = not alarm_armed
    query.edit_message_text('Alarm has been: ' + ('armed' if alarm_armed else 'disarmed'), reply_markup=reply_markup)
  elif query.data == 'watch':
    global listen_to_motion
    global alerts
    listen_to_motion = not listen_to_motion
    alerts = not alerts
    query.edit_message_text('Watching for motion: ' + str(listen_to_motion), reply_markup=reply_markup)

def send(updater, user_id, message):
  updater.bot.sendMessage(chat_id=user_id, text=message)

def wag():
  for i in range(3):
    servo.ChangeDutyCycle(LEFT)
    time.sleep(0.7)
    servo.ChangeDutyCycle(MIDDLE)
    time.sleep(0.7)

def main() -> None:
  # get the TELEGRAM_API_TOKEN from the .env file
  load_dotenv()
  TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
  MY_USER_ID = os.getenv("MY_USER_ID")
  
  # create updater and dispatcher
  updater = Updater(token=TELEGRAM_API_TOKEN, use_context=True)
  dispatcher = updater.dispatcher

  # on different commands - answer in Telegram
  dispatcher.add_handler(CommandHandler("start", start))
  dispatcher.add_handler(CommandHandler("help", help_command))
  dispatcher.add_handler(CommandHandler("commands", commands))
  dispatcher.add_handler(CommandHandler("watch", watch))
  dispatcher.add_handler(CommandHandler("arm", arm))
  updater.dispatcher.add_handler(CallbackQueryHandler(button))

  # on non command i.e message - echo the message on Telegram
  dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

  # Start the Bot
  updater.start_polling()
  
  try:
    while True:
      while alarm_armed:
        print("Waiting for motion...")
        if listen_to_motion: send(updater, MY_USER_ID, "Waiting for motion...")
        while alarm_armed and GPIO.input(GPIO_PIR) == 0:
          startTime = time.time()
        
        print("Motion detected!")
        if listen_to_motion: send(updater, MY_USER_ID, "Motion detected!")
        while alarm_armed and GPIO.input(GPIO_PIR) == 1:
          stopTime = time.time()
          
        motionTime = stopTime - startTime
        print("Motion lasted: %.2f seconds\n" % motionTime)
        if listen_to_motion: send(updater, MY_USER_ID, "Motion lasted: %.2f seconds\n" % motionTime)
        if alerts and motionTime > 0: send(updater, MY_USER_ID, """-=ALERT=-
Motion detected!
Motion lasted: %.2f seconds
""" % motionTime)
        wag()
        
  except KeyboardInterrupt:
    pass

  # Run the bot until you press Ctrl-C or the process receives SIGINT,
  # SIGTERM or SIGABRT. This should be used most of the time, since
  # start_polling() is non-blocking and will stop the bot gracefully.
  updater.idle()
  GPIO.cleanup()


if __name__ == '__main__':
  main()