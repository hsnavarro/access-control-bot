import os
import logging
import dataset
import datetime
from telegram import *
from telegram.ext import *
from bot_admin import *

db = dataset.connect("sqlite:///access-control.db")
token = os.environ['TOKEN']
updater = Updater(token=token)

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

#Acess dispatcher
dispatcher = updater.dispatcher

#Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Access Class
class Access(object):
  def __str__(self):
    return "RFID: {0}, Dia da semana: {1}, Início: {2}, Término: {3}".format(str(self.rfid), self.weekday, self.start_time, self.end_time)

  def __init__(self, rfid, weekday, start_time="00:00", end_time="23:59"):
    self.rfid = rfid
    self.weekday = weekday
    self.start_time = start_time
    self.end_time = end_time

# Method to start the bot
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, 
                     text="Bot para controle de Acesso - Projeto de Laboratório de Sistemas Embarcados")

# Show access list
def access_list(bot, update):
  access_db = db["access"]
  access_list = list(access_db.all())

  if len(access_list) == 0:
    bot.send_message(
      chat_id = update.message.chat_id,
      text="Lista de acesso vazia")
  else:
    msg = "*Lista de acesso*\n"

    for access in access_list:
      access_object = Access(access['RFID'], access['weekday'], access['start_time'], access['end_time'])
      msg += str(access_object) + "\n"

    bot.send_message(
      chat_id = update.message.chat_id,
      text = msg,
      parse_mode = ParseMode.MARKDOWN,
      disable_web_page_preview=True
    )

def add_access_internal(update, access):
  access_db = db['access']
  access_db.upsert(
    dict(
      RFID = access.rfid,
      weekday = access.weekday,
      start_time = access.start_time,
      end_time = access.end_time,
    ),
    ['RFID', 'weekday']
  )

  msg = "*Acesso adicionado*\n"
  msg += str(access) + "\n"

  update.message.reply_text(
    msg,
    parse_mode = ParseMode.MARKDOWN,
    disable_web_page_preview=True
  )

def is_between(l_hours, l_minutes, r_hours, r_minutes, hours, minutes):
  l = l_hours * 60 + l_minutes
  r = r_hours * 60 + r_minutes

  t = hours * 60 + minutes

  if l <= t and t <= r:
    return True
  
  return False

def get_access_internal(rfid):
  date = datetime.datetime.now()
  weekday = WEEKDAYS[date.weekday()]
  hours = date.hour
  minutes = date.minute

  access_db = db['access']
  access_infos = list(access_db.find(RFID=rfid, weekday=weekday))

  if len(access_infos) == 0:
    return False 

  access_info = access_infos[0]
  start_time = access_info['start_time']
  end_time = access_info['end_time']

  start_time_hours, start_time_minutes = map(int, start_time.split(':'))
  end_time_hours, end_time_minutes = map(int, end_time.split(':'))

  if is_between(start_time_hours, start_time_minutes,
                end_time_hours, end_time_minutes,
                hours, minutes):
    return True

  return False

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
    access = Access(rfid, weekday)
    add_access_internal(update, access)

@restricted
def add_access_by_time(bot, update, args):
  if len(args) < 3:
    update.effective_message.reply_text(
      "Comando incorreto.\nUso: /add_access_by_time <rfid> <start_time> <end_time>"
    )
    return

  try:
    rfid = int(args[0])
    start_time = args[1]
    end_time = args[2]
  except ValueError:
    update.effective_message.reply_text("RFID é para ser um número!")
    return

  for weekday in WEEKDAYS:
    access = Access(rfid, weekday, start_time, end_time)
    add_access_internal(update, access)

@restricted
def add_access_by_weekday(bot, update, args):
  if len(args) < 2:
    update.effective_message.reply_text(
      "Comando incorreto.\nUso: /add_access_by_weekday <rfid> <weekday>"
    )
    return

  try:
    rfid = int(args[0])
    weekday = args[1]
  except ValueError:
    update.effective_message.reply_text("RFID é para ser um número!")
    return

  access = Access(rfid, weekday)
  add_access_internal(update, access)

@restricted
def add_access_by_time_and_weekday(bot, update, args):
  if len(args) < 4:
    update.effective_message.reply_text(
      "Comando incorreto.\nUso: /add_access_by_time_and_weekday <rfid> <start_time> <end_time> <weekday>"
    )
    return

  try:
    rfid = int(args[0])
    start_time = args[1]
    end_time = args[2]
    weekday = args[3]
  except ValueError:
    update.effective_message.reply_text("RFID é para ser um número!")
    return

  access = Access(rfid, weekday, start_time, end_time)
  add_access_internal(update, access)

def get_access(bot, update, args):
  if len(args) < 1:
    update.effective_message.reply_text(
      "Comando incorreto.\nUso: /get_access <rfid>"
    )
    return

  try:
    rfid = int(args[-1])
  except ValueError:
    update.effective_message.reply_text("RFID é para ser um número!")
    return

  if get_access_internal(rfid):
    bot.send_message(chat_id=update.message.chat_id,
                       text="Acesso Autorizado")
  else:
    bot.send_message(chat_id=update.message.chat_id,
                       text="Acesso Negado")

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
dispatcher.add_handler(CommandHandler('add_access_by_time', add_access_by_time, pass_args=True))
dispatcher.add_handler(CommandHandler('add_access_by_weekday', add_access_by_weekday, pass_args=True))
dispatcher.add_handler(CommandHandler('add_access_by_time_and_weekday', add_access_by_time_and_weekday, pass_args=True))
dispatcher.add_handler(CommandHandler('get_access', get_access, pass_args=True))
dispatcher.add_handler(CommandHandler('reset', reset))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

#Start bot
print("Bot rodando...")
updater.start_polling()