import os
import logging
from dotenv import load_dotenv
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

GPIO_PIR = 16
GPIO.setup(GPIO_PIR, GPIO.IN)

# enable logging
logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
listen_to_motion = False

def start(update: Update, context: CallbackContext) -> None:
  user = update.effective_user
  update.message.reply_markdown_v2(
    fr'Hi {user.mention_markdown_v2()}\!'
    f'Use /help to get a list of commands',
    reply_markup=ForceReply(selective=True),
  )

def help_command(update: Update, context: CallbackContext) -> None:
  update.message.reply_text('Help!')

# bot functions
def echo(update: Update, context: CallbackContext) -> None:
  update.message.reply_text(update.message.text)

def settings(update: Update, context: CallbackContext) -> None:
  keyboard = [
    [
        InlineKeyboardButton("Option 1", callback_data='1'),
        InlineKeyboardButton("Option 2", callback_data='2'),
    ],
    [InlineKeyboardButton("Option 3", callback_data='3')],
  ]
  
  reply_markup = InlineKeyboardMarkup(keyboard)

  update.message.reply_text('Please choose:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
  """Parses the CallbackQuery and updates the message text."""
  query = update.callback_query

  # CallbackQueries need to be answered, even if no notification to the user is needed
  # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
  query.answer()

  query.edit_message_text(text=f"Selected option: {query.data}")

def main() -> None:
  # get the TELEGRAM_API_TOKEN from the .env file
  load_dotenv()
  TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
  
  # create updater and dispatcher
  updater = Updater(token=TELEGRAM_API_TOKEN, use_context=True)
  dispatcher = updater.dispatcher

  # on different commands - answer in Telegram
  dispatcher.add_handler(CommandHandler("start", start))
  dispatcher.add_handler(CommandHandler("help", help_command))
  dispatcher.add_handler(CommandHandler("settings", settings))
  updater.dispatcher.add_handler(CallbackQueryHandler(button))

  # on non command i.e message - echo the message on Telegram
  dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

  # Start the Bot
  updater.start_polling()
  
  try:
    while True:
      while listen_to_motion:
        print("Waiting for motion...")
        Update.message.reply_text('Waiting for motion...')
        while GPIO.input(GPIO_PIR) == 0:
          startTime = time.time()
        
        print("Motion detected!")
        while GPIO.input(GPIO_PIR) == 1:
          stopTime = time.time()
          
        motionTime = stopTime - startTime
        print("Motion lasted: %.2f seconds\n" % motionTime)
  except KeyboardInterrupt:
    pass

  # Run the bot until you press Ctrl-C or the process receives SIGINT,
  # SIGTERM or SIGABRT. This should be used most of the time, since
  # start_polling() is non-blocking and will stop the bot gracefully.
  updater.idle()
  GPIO.cleanup()


if __name__ == '__main__':
  main()