from functools import wraps
from telegram import *
from telegram.ext import *

hsnavarro_user_id = 505299455
ADMIN = [hsnavarro_user_id]

def restricted(func):
  @wraps(func)
  def wrapped(bot, update, *args, **kwargs):
    user_id = update.effective_user.id
    if user_id not in ADMIN:
      update.effective_message.reply_text("Acesso Negado")
      return
    return func(bot, update, *args, **kwargs)
  return wrapped
