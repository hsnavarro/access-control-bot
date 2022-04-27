import os
import logging
import dataset
from telegram import *
from telegram.ext import *
from bot_admin import *

db = dataset.connect("sqlite:///access-control.db")
token = os.environ['TOKEN']
updater = Updater(token=token)

WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

#Acess dispatcher
dispatcher = updater.dispatcher

#Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Method to start the bot
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, 
                     text="Bot para controle de Acesso - Projeto de Laboratório de Sistemas Embarcados")

#Show access list
def access_list(bot, update):
  access_db = db["access"]
  access_list = list(access_db.all())

  if len(access_list) == 0:
    bot.send_message(
      chat_id = update.message.chat_id,
      text="Lista de acesso vazia")
  else:
    msg = "*Lista de Acesso*\n"

    for access in access_list:
      msg += "RFID: " + str(access['RFID'])
      msg += " Dia da semana: " + access['weekday']
      msg += " Início: " + access['start_time']
      msg += " Término: " + access['end_time'] + "\n"

    bot.send_message(
      chat_id = update.message.chat_id,
      text = msg,
      parse_mode = ParseMode.MARKDOWN,
      disable_web_page_preview=True
    )

def add_access_internal(update, rfid, weekday, start_time, end_time):
  access_db = db['access']
  access_db.upsert(
    dict(
      RFID=rfid, 
      weekday=weekday, 
      start_time=start_time, 
      end_time=end_time
    ), 
    ['RFID', 'weekday']
  )

  msg = "*Acesso adicionado*\n"
  msg += "RFID: " + str(rfid)
  msg += " Dia da semana: " + weekday
  msg += " Início: " + start_time
  msg += " Término: " + end_time + "\n"

  update.message.reply_text(
    msg,
    parse_mode = ParseMode.MARKDOWN,
    disable_web_page_preview=True
  )

@restricted
def add_access(bot, update, args):
  if len(args) < 1:
    update.effective_message.reply_text(
      "Comando incorreto.\nUso: /add_access <rfid>"
    )
    return

  try:
    rfid = int(args[-1])
  except ValueError:
    update.effective_message.reply_text("RFID é para ser um número!")
    return

  for weekday in WEEKDAYS:
    add_access_internal(update, rfid, weekday, start_time="00:00", end_time="23:59")

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, 
                     text="Comando não reconhecido.")

@restricted
def reset(bot, update):
    access_db = db['access']
    if len(access_db) == 0:
      bot.send_message(chat_id=update.message.chat_id,
                       text="Lista de acesso está vazia")
    else:
      auxiliar = list(access_db.all())

      for access in auxiliar:
        access_db.delete(RFID=access['RFID'], weekday=access['weekday'])

      bot.send_message(chat_id=update.message.chat_id,
                      text="Lista de acesso foi resetada")

#Add Handlers
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('access_list', access_list))
dispatcher.add_handler(CommandHandler('add_access', add_access, pass_args=True))
dispatcher.add_handler(CommandHandler('reset', reset))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

#Start bot
print("Bot rodando...")
updater.start_polling()