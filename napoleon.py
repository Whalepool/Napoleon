#!/usr/bin/env python3
# A Simple way to send a message to telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pprint import pprint
from functools import wraps
from future.builtins import bytes
import argparse
import telegram
import sys
import requests
import json
import shlex
import hashlib
import urllib.request 
import time
import hmac
import subprocess

#custom modules

import utils.loadconfig as config 
import utils.wplogging as wplogging
import utils.wprestricted as wprestricted
import exchanges.bitmex as bitmex 
import exchanges.onebroker as onebroker



#################################
# Begin bot.. 
bot = telegram.Bot(token=config.TELEGRAM_BOT_TOKEN)

def error(bot, update, error):
    wplogging.logger.warn('Update "%s" caused error "%s"' % (update, error))


#################################
# Bot commands
@wprestricted.restricted
def help(bot, update):

	# Logging
	wplogging.logger.info("/help - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Output
	msg   =  str(update.message.chat.first_name)+" :: "+str(update.message.chat.id)+"\n"

	msg  +=  "*User*\n"
	msg  +=  "/id`                   `- get your telegram userid \n"
	msg  +=  "/debug`                `- output telegram bot variables to console \n"

	msg  +=  "*1BROKER* \n"

	msg  +=  "/onebroker\_gettxlog`             `- last 10 transactions \n"
	msg  +=  "/onebroker\_getbalances`          `- summary of balances \n"
	msg  +=  "/onebroker\_getpositions`         `- summary of positions \n" 

	msg  +=  "_Orders_\n"
	msg  +=  "/onebroker\_openorders`          `- list open orders \n"
	msg  +=  "/onebroker\_createposition`      `- open a long/short [args] \n"
	msg  +=  "/onebroker\_cancelorder`         `- cancel an order \n"

	msg  +=  "_Position_\n"
	msg  +=  "/onebroker\_openpositions`       `- list open positions \n"
	msg  +=  "/onebroker\_editposition`        `- edit a position [args] \n"
	msg  +=  "/onebroker\_closeposition`       `- close a position [args] \n"
	msg  +=  "/onebroker\_cancelcloseposition` `- cancel a position trying to close [args] \n"
	msg  +=  "/onebroker\_positionhistory`     `- historic positions sorted by closing date \n"

	msg  +=  "_Market_\n"
	msg  +=  "/onebroker\_marketcategories`    `- list market categories \n"
	msg  +=  "/onebroker\_marketlist`          `- list markets for category [args] \n"
	msg  +=  "/onebroker\_marketdetails`       `- details of the market [args] \n"

	msg  +=  "*SHITMEX* \n"
	msg  +=  "/bitmex\_fullorder`                  `- make full order [args] \n"
	msg  +=  "/bitmex\_order`                  `- make order [args] \n"
	msg  +=  "/bitmex\_getbalance`             `- get bitmex account balance \n"
	msg  +=  "/bitmex\_listorders`             `- get bitmex open order list \n"
	msg  +=  "/bitmex\_positionlist`           `- get bitmex open position list \n"
	msg  +=  "/bitmex\_cancelorders`           `- cancel all open bitmex orders for a symbol \n"
	msg  +=  "/bitmex\_cancelorder`           `- cancel one open bitmex order, give orderID \n"
	msg  +=  "/bitmex\_tradehistory`             `- get bitmex last 5 executions \n"
	bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 



def id(bot, update):

	# Logging
	wplogging.logger.info("/id - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Output
	msg   =  str(update.message.chat.first_name)+" :: "+str(update.message.chat.id)+"\n"
	update.message.reply_text(msg,parse_mode="Markdown")



@wprestricted.restricted
def debug(bot, update):

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	wplogging.logger.info("update.message")
	pprint(update.message.__dict__, indent=4)
	wplogging.logger.info("update.message.chat")
	pprint(update.message.chat.__dict__, indent=4)
	wplogging.logger.info("update.message.entities")
	pprint(update.message.chat.__dict__, indent=4)
	wplogging.logger.info("update.message.from_user")
	pprint(update.message.from_user.__dict__, indent=4)

	update.message.reply_text("Sent debugging info to command line")


#################################
# Command Handlers
wplogging.logger.info("Setting  command handlers")
updater = Updater(bot=bot,workers=10)
dp      = updater.dispatcher

# PUBLIC
dp.add_handler(CommandHandler('id', id))

# PRIVATE 
dp.add_handler(CommandHandler('help', help))
dp.add_handler(CommandHandler('debug', debug))


# 1BROKER 

# User 
dp.add_handler(CommandHandler('onebroker_gettxlog', onebroker.onebroker_gettxlog))
dp.add_handler(CommandHandler('onebroker_getbalances', onebroker.onebroker_getbalances))
dp.add_handler(CommandHandler('onebroker_getpositions', onebroker.onebroker_getpositions))

# Order
dp.add_handler(CommandHandler('onebroker_openorders', onebroker.onebroker_openorders))
dp.add_handler(CommandHandler('onebroker_createposition', onebroker.onebroker_createposition))
dp.add_handler(CommandHandler('onebroker_cancelorder', onebroker.onebroker_cancelorder))

# Position
dp.add_handler(CommandHandler('onebroker_openpositions', onebroker.onebroker_openpositions))
dp.add_handler(CommandHandler('onebroker_editposition', onebroker.onebroker_editposition))
dp.add_handler(CommandHandler('onebroker_closeposition', onebroker.onebroker_closeposition))
dp.add_handler(CommandHandler('onebroker_cancelcloseposition', onebroker.onebroker_cancelcloseposition))
dp.add_handler(CommandHandler('onebroker_positionhistory', onebroker.onebroker_positionhistory))

# Market
dp.add_handler(CommandHandler('onebroker_marketcategories', onebroker.onebroker_marketcategories))
dp.add_handler(CommandHandler('onebroker_marketlist', onebroker.onebroker_marketlist))
dp.add_handler(CommandHandler('onebroker_marketdetails', onebroker.onebroker_marketdetails))


# SHITMEX
dp.add_handler(CommandHandler('bitmex_getbalance', bitmex.bitmex_getbalance))
dp.add_handler(CommandHandler('bitmex_listorders', bitmex.bitmex_listorders))
dp.add_handler(CommandHandler('bitmex_positionlist', bitmex.bitmex_positionlist))
dp.add_handler(CommandHandler('bitmex_cancelorder', bitmex.bitmex_cancelorder))
dp.add_handler(CommandHandler('bitmex_cancelorders', bitmex.bitmex_cancelorders))
dp.add_handler(CommandHandler('bitmex_fullorder', bitmex.bitmex_fullorder))
dp.add_handler(CommandHandler('bitmex_order', bitmex.bitmex_order))
dp.add_handler(CommandHandler('bitmex_tradehistory', bitmex.bitmex_tradehistory))

# log all errors
dp.add_error_handler(error)



#################################
# Polling 
wplogging.logger.info("Starting polling")
updater.start_polling()
