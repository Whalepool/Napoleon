#1Broker affiliate account commands
#All renamed to onebroker_ prefix



from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pprint import pprint
from functools import wraps
from future.builtins import bytes
import argparse
import logging
import telegram
import sys
import requests
import json
import shlex
import hashlib
import urllib.request 
import time
import hmac


#custom

import utils.loadconfig as config 
import utils.wprestricted as wprestricted
import utils.wplogging as wplogging



@wprestricted.restricted
def onebroker_gettxlog(bot, update):

	# Logging
	wplogging.logger.info("/onebroker_gettxlog - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Request
	url     = "https://1broker.com/api/v2/user/transaction_log.php?token="+config.BROKER_API_TOKEN+"&pretty=1&limit=10"
	request = requests.get(url).json()

	# API Error 
	if request['error'] == True:
		msg = 'Error fetching transaction log: '+str(request['error_code'])+", Description: "+request['error_message']

		wplogging.logger.info(update.message.chat.first_name+" "+msg)
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

		return 

	# Return MSG
	resp = request['response']
	msg  = config.MSG_HEADER_ONEBROKER

	for d in resp:
		msg += "*Date: "+d['date']+"*/\n"
		msg += "Type: "+d['type']+"\n"
		msg += "Balance delta: "+d['balance_delta']+"\n"
		msg += "Balance new: "+d['balance_new']+"\n"
		msg += "Desc: "+d['description']+"\n"
		msg += "`----------------`\n"

	bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 



@wprestricted.restricted
def onebroker_getbalances(bot, update):

	# Logging
	wplogging.logger.info("/onebroker_getbalances - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Request
	url     = "https://1broker.com/api/v2/user/overview.php?token="+config.BROKER_API_TOKEN+"&pretty=1"
	request = requests.get(url).json()

	# API Error 
	if request['error'] == True:
		msg = 'Error fetching overview: '+str(request['error_code'])+", Description: "+request['error_message']

		wplogging.logger.info(update.message.chat.first_name+" "+msg)
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

		return 

	# Return MSG
	resp = request['response']
	msg  = config.MSG_HEADER_ONEBROKER
	msg += "Balance: "+resp['balance']+"\n"
	msg += "Orders worth: "+resp['orders_worth']+"\n"
	msg += "Positions worth: "+resp['positions_worth']+"\n"
	msg += "Net worth: "+resp['net_worth']

	bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 



@wprestricted.restricted
def onebroker_getpositions(bot, update):

	# Logging
	wplogging.logger.info("/onebroker_getpositions - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Request
	url     = "https://1broker.com/api/v2/user/overview.php?token="+config.BROKER_API_TOKEN+"&pretty=1"
	request = requests.get(url).json()

	# API Error 
	if request['error'] == True:
		msg = 'Error fetching overview: '+str(request['error_code'])+", Description: "+request['error_message']

		wplogging.logger.info(update.message.chat.first_name+" "+msg)
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

		return 


	# Return MSG
	resp = request['response']['positions_open']
	msg = config.MSG_HEADER_ONEBROKER

	if len(resp) == 0:
                msg  += "Currently no open positions"
                bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 
                return

	for d in resp:
		msg += "*"+d['symbol']+"*: "+d['direction']+", entry: "+d['entry_price']+", s/l: "+d['stop_loss']+", margin: "+d['margin']+", P&L: "+d['profit_loss_percent']+"% \n"

	bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1)



@wprestricted.restricted
def onebroker_openorders(bot, update):

	# Logging
	wplogging.logger.info("/onebroker_openorders - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Request
	url     = "https://1broker.com/api/v2/order/open.php?token="+config.BROKER_API_TOKEN+"&pretty=1"
	request = requests.get(url).json()

	# API Error 
	if request['error'] == True:
		msg = 'Error fetching open orders, log: '+str(request['error_code'])+", Description: "+request['error_message']

		wplogging.logger.info(update.message.chat.first_name+" "+msg)
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

		return 

	# Return MSG
	resp = request['response']

	msg  = config.MSG_HEADER_ONEBROKER

	# No open orders ? 
	if len(resp) == 0:
		msg  += "Currently no open orders"
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 
		return 

	# Build the message of open orders

	for d in resp:
		msg += "Order Id: "+str(d['order_id'])+"\n"
		msg += "Symbol: "+str(d['symbol'])+"\n"
		msg += "Margin: "+str(d['margin'])+"\n"
		msg += "Leverage: "+str(d['leverage'])+"\n"
		msg += "Direction: "+str(d['direction'])+"\n"
		msg += "Order Type: "+str(d['order_type'])+"\n"
		msg += "Order Type Param: "+str(d['order_type_parameter'])+"\n"
		msg += "Stop Loss: "+str(d['stop_loss'])+"\n"
		msg += "Take Profit: "+str(d['take_profit'])+"\n"
		msg += "Shared: "+str(d['shared'])+"\n"
		msg += "Date Created: "+str(d['date_created'])+"\n"
		msg += "`----------------`\n"

	bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 




@wprestricted.restricted
def onebroker_createposition(bot, update):

	# Logging
	wplogging.logger.info("/onebroker_createposition - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Parser setup
	parser = argparse.ArgumentParser(description='Parse position input')
	parser.add_argument('-symbol', type=str, required=True)
	parser.add_argument('-margin', type=float, help='Amount to bet in btc', required=True)
	parser.add_argument('-direction', choices=['long','short'], type=str, required=True)
	parser.add_argument('-ordertype', choices=['market','limit','stop_entry'], type=str, required=True)
	parser.add_argument('-ordertypeparameter', type=float, help='Parameter for the specified ordertype. Not required for \'Market\' orders.')
	parser.add_argument('-stop_loss', type=float, help='Stop Loss for the position, once opened.')
	parser.add_argument('-take_profit', type=float, help='Take Profit for the position, once opened.')


	help_msg  = "*/onebroker_createposition [args]* [example](https://1broker.com/?c=en/content/api-documentation#order-create) \n"
	help_msg += "`-symbol=\"xxx\"` (str) \n" 
	help_msg += "`-margin=\"0.1\"` (float) \n" 
	help_msg += "`-direction=\"long\"` 'long' or 'short' \n" 
	help_msg += "`-ordertype=\"limit\"` 'market', 'limit', or 'stop\\_entry' \n" 
	help_msg += "`-ordertypeparameter=\"5\"` (float) \n" 
	help_msg += "`-stop_loss=\"0.012\"` _optional_ (float) \n" 
	help_msg += "`-take_profit=\"0.012\"` _optional_ (float) \n" 

	# Split the arguments passed to it
	split = update.message.text.split(' ', 1)

	# Got no arguments passed to it
	if len(split) == 1:
		wplogging.logger.info("No arguments passed")
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return


	# We have arguments passed
	# Parse them
	try:
		
		# Log 
		wplogging.logger.info("Trying to parse args: "+update.message.text) 

		# Parse
		args = parser.parse_args(shlex.split(split[1]))


		# Request
		url      = "https://1broker.com/api/v2/order/create.php?token="+config.BROKER_API_TOKEN+"&pretty=1"
		url     += "&symbol="+str(args.symbol)
		url     += "&margin="+str(args.margin)
		url     += "&direction="+str(args.direction)
		url     += "&leverage=3"
		url     += "&shared=true" 
		url     += "&order_type="+str(args.ordertype)
		url     += "&order_type_parameter="+str(args.ordertypeparameter)
		if args.stop_loss:
			url += "&stop_loss="+str(args.stop_loss)
		if args.take_profit:
			url += "&take_profit="+str(args.take_profit)


		request  = requests.get(url).json()

		# API Error 
		if request['error'] == True:
			msg = 'Error creating order, log: '+str(request['error_code'])+", Description: "+request['error_message']

			wplogging.logger.info(update.message.chat.first_name+" "+msg)
			bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

			return 

		# Return MSG
		resp = request['response']

		# Build the message of open orders
		msg  = '*Created order #'+str(resp['order_id'])+"*\n"
		msg += "Symbol: `"+str(resp['symbol'])+"`\n"
		msg += "Margin: "+str(resp['margin'])+"\n"
		msg += "Leverage: "+str(resp['leverage'])+"\n"
		msg += "Direction: "+str(resp['direction'])+"\n"
		msg += "Order Type: "+str(resp['order_type'])+"\n"
		msg += "Order Type Param: "+str(resp['order_type_parameter'])+"\n"
		msg += "Stop Loss: "+str(resp['stop_loss'])+"\n"
		msg += "Take Profit: "+str(resp['take_profit'])+"\n"
		msg += "Shared: "+str(resp['shared'])+"\n"
		msg += "Date Created: "+str(resp['date_created'])+"\n"

		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 



	except SystemExit:
		wplogging.logger.info("Failed to parse args: "+update.message.text)
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return


@wprestricted.restricted
def onebroker_cancelorder(bot, update):

	# Logging
	wplogging.logger.info("/onebroker_cancelorder - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Parser setup
	parser = argparse.ArgumentParser(description='Parse position input')
	parser.add_argument('-orderid', type=int, required=True)

	help_msg  = "*/onebroker_cancelorder [args]* [example](https://1broker.com/?c=en/content/api-documentation#order-cancel) \n"
	help_msg += "`-orderid=\"xxx\"` (int) \n" 

	# Split the arguments passed to it
	split = update.message.text.split(' ', 1)

	# Got no arguments passed to it
	if len(split) == 1:
		wplogging.logger.info("No arguments passed")
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return


	# We have arguments passed
	# Parse them
	try:
		
		# Log 
		wplogging.logger.info("Trying to parse args: "+update.message.text) 

		# Parse
		args = parser.parse_args(shlex.split(split[1]))


		# Request
		url      = "https://1broker.com/api/v2/order/cancel.php?token="+config.BROKER_API_TOKEN+"&pretty=1"
		url     += "&order_id="+str(args.orderid)


		request  = requests.get(url).json()

		# API Error 
		if request['error'] == True:
			msg = 'Error cancelling order order, log: '+str(request['error_code'])+", Description: "+request['error_message']

			wplogging.logger.info(update.message.chat.first_name+" "+msg)
			bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

			return 

		# Return MSG
		resp = request['response']

		# Build the message of open orders
		msg  = 'Order cancelled'

		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 



	except SystemExit:
		wplogging.logger.info("Failed to parse args: "+update.message.text)
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return



@wprestricted.restricted
def onebroker_openpositions(bot, update):

	# Logging
	wplogging.logger.info("/onebroker_openpositions - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Request
	url     = "https://1broker.com/api/v2/position/open.php?token="+config.BROKER_API_TOKEN+"&pretty=1"
	request = requests.get(url).json()

	# API Error 
	if request['error'] == True:
		msg = 'Error fetching open position, log: '+str(request['error_code'])+", Description: "+request['error_message']

		wplogging.logger.info(update.message.chat.first_name+" "+msg)
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

		return 


	# Return MSG
	resp = request['response']
	msg  = config.MSG_HEADER_ONEBROKER
	# + len(resp)

	# No open positions ? 
	if len(resp) == 0:
		msg += "Currently no open positions"
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 
		return 

	# Build the message of open orders

	for d in resp:
		msg += "*Position Id: "      +str(d['position_id'])+"*\n"
		msg += "Order Id: "          +str(d['order_id'])+"\n"
		msg += "Symbol: *"           +str(d['symbol'])+"*\n"
		msg += "Margin: "            +str(d['margin'])+"\n"
		msg += "Leverage: "          +str(d['leverage'])+"\n"
		msg += "Direction: "         +str(d['direction'])+"\n"
		msg += "Entry Price: "       +str(d['entry_price'])+"\n"
		msg += "Profit Loss: "       +str(d['profit_loss'])+"\n"
		msg += "Profit Loss %: "     +str(d['profit_loss_percent'])+"\n"
		msg += "Mark Close: "        +str(d['market_close'])+"\n"
		msg += "Stop Loss: "         +str(d['stop_loss'])+"\n"
		msg += "Take Profit: "       +str(d['take_profit'])+"\n"
		msg += "Trailing Stop loss: "+str(d['trailing_stop_loss'])+"\n"
		msg += "Shared: "            +str(d['shared'])+"\n"
		msg += "Copy of: "           +str(d['copy_of'])+"\n"
		msg += "Date Created: "      +str(d['date_created'])+"\n"
		msg += "`----------------`\n"

	bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 




@wprestricted.restricted
def onebroker_editposition(bot, update):

	# Logging
	wplogging.logger.info("/onebroker_editposition - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Parser setup
	parser = argparse.ArgumentParser(description='Parse position input')
	parser.add_argument('-positionid', type=int, required=True)
	parser.add_argument('-stop_loss', type=float)
	parser.add_argument('-take_profit', type=float)
	parser.add_argument('-trailing_stop_loss', type=str)

	help_msg  = "*/onebroker_editposition [args]* [example](https://1broker.com/?c=en/content/api-documentation#position-edit) \n"
	help_msg += "`-positionid=\"xxx\"` (int) \n" 
	help_msg += "`-stop_loss=\"xxx\"` (float) \n" 
	help_msg += "`-take_profit=\"xxx\"` (float) \n" 
	help_msg += "`-trailing_stop_loss=\"true\"` (str) \n" 

	# Split the arguments passed to it
	split = update.message.text.split(' ', 1)

	# Got no arguments passed to it
	if len(split) == 1:
		wplogging.logger.info("No arguments passed")
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return


	# We have arguments passed
	# Parse them
	try:
		
		# Log 
		wplogging.logger.info("Trying to parse args: "+update.message.text) 

		# Parse
		args = parser.parse_args(shlex.split(split[1]))

		# Request
		url      = "https://1broker.com/api/v2/position/edit.php?token="+config.BROKER_API_TOKEN+"&pretty=1"
		url     += "&position_id="+str(args.positionid)
		if args.stop_loss:
			url += "&stop_loss="+str(args.stop_loss)
		if args.take_profit:
			url += "&take_profit="+str(args.take_profit)
		if args.trailing_stop_loss:
			url += "&trailing_stop_loss="+str(args.trailing_stop_loss)

		request  = requests.get(url).json()

		# API Error 
		if request['error'] == True:
			msg = 'Error editing position, log: '+str(request['error_code'])+", Description: "+request['error_message']

			wplogging.logger.info(update.message.chat.first_name+" "+msg)
			bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

			return 

		# Return MSG
		resp = request['response']

		# Build the message of open orders
		msg  = '*Position edited*\n'
		msg += "Positiond Id: "+str(resp['position_id'])
		msg += "Stop Loss: "+str(resp['stop_loss'])
		msg += "Take Profit: "+str(resp['take_profit'])
		msg += "Trailing stop loss: "+str(resp['trailing_stop_loss'])

		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 



	except SystemExit:
		wplogging.logger.info("Failed to parse args: "+update.message.text)
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return



@wprestricted.restricted
def onebroker_closeposition(bot, update):

	# Logging
	wplogging.logger.info("/onebroker_closeposition - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Parser setup
	parser = argparse.ArgumentParser(description='Parse position input')
	parser.add_argument('-positionid', type=int, required=True)

	help_msg  = "*/onebroker_closeposition [args]* [example](https://1broker.com/?c=en/content/api-documentation#position-close) \n"
	help_msg += "`-positionid=\"xxx\"` (int) \n" 

	# Split the arguments passed to it
	split = update.message.text.split(' ', 1)

	# Got no arguments passed to it
	if len(split) == 1:
		wplogging.logger.info("No arguments passed")
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return


	# We have arguments passed
	# Parse them
	try:
		
		# Log 
		wplogging.logger.info("Trying to parse args: "+update.message.text) 

		# Parse
		args = parser.parse_args(shlex.split(split[1]))


		# Request
		url      = "https://1broker.com/api/v2/position/close.php?token="+config.BROKER_API_TOKEN+"&pretty=1"
		url     += "&position_id="+str(args.positionid)


		request  = requests.get(url).json()

		# API Error 
		if request['error'] == True:
			msg = 'Error closing position, log: '+str(request['error_code'])+", Description: "+request['error_message']

			wplogging.logger.info(update.message.chat.first_name+" "+msg)
			bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

			return 

		# Return MSG
		resp = request['response']

		# Build the message of open orders
		msg  = 'Closing position '+str(args.positionid)

		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 



	except SystemExit:
		wplogging.logger.info("Failed to parse args: "+update.message.text)
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return



@wprestricted.restricted
def onebroker_cancelcloseposition(bot, update):

	# Logging
	wplogging.logger.info("/onebroker_cancelcloseposition - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Parser setup
	parser = argparse.ArgumentParser(description='Parse position input')
	parser.add_argument('-position_id', type=int, required=True)

	help_msg  = "*/onebroker_cancelcloseposition [args]* [example](https://1broker.com/?c=en/content/api-documentation#position-close-cancel) \n"
	help_msg += "`-positionid=\"xxx\"` (int) \n"  

	# Split the arguments passed to it
	split = update.message.text.split(' ', 1)

	# Got no arguments passed to it
	if len(split) == 1:
		wplogging.logger.info("No arguments passed")
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return


	# We have arguments passed
	# Parse them
	try:
		
		# Log 
		wplogging.logger.info("Trying to parse args: "+update.message.text) 

		# Parse
		args = parser.parse_args(shlex.split(split[1]))


		# Request
		url      = "https://1broker.com/api/v2/position/close_cancel.php?token="+config.BROKER_API_TOKEN+"&pretty=1"
		url     += "&position_id="+str(args.positionid)


		request  = requests.get(url).json()

		# API Error 
		if request['error'] == True:
			msg = 'Error cancelling cancel position, log: '+str(request['error_code'])+", Description: "+request['error_message']

			wplogging.logger.info(update.message.chat.first_name+" "+msg)
			bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

			return 

		# Return MSG
		resp = request['response']

		# Build the message of open orders
		msg  = 'Cancelling Closing position '+str(args.positionid)

		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


	except SystemExit:
		wplogging.logger.info("Failed to parse args: "+update.message.text)
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return



@wprestricted.restricted
def onebroker_positionhistory(bot, update):

	# Logging
	wplogging.logger.info("/onebroker_positionhistory - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Request
	url     = "https://1broker.com/api/v2/position/history.php?token="+config.BROKER_API_TOKEN+"&pretty=1"
	request = requests.get(url).json()

	# API Error 
	if request['error'] == True:
		msg = 'Error fetching position history, log: '+str(request['error_code'])+", Description: "+request['error_message']

		wplogging.logger.info(update.message.chat.first_name+" "+msg)
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

		return 

	# Return MSG
	resp = request['response']
	# No open orders ? 
	if len(resp) == 0:
		bot.sendMessage(chat_id=update.message.chat.id,text="No position history returned",parse_mode="Markdown",disable_web_page_preview=1) 
		return 

	# Build the message of open orders
	msg  = config.MSG_HEADER_ONEBROKER

	for d in resp:
		msg += "*Position Id: "      +str(d['position_id'])+"*\n"
		msg += "Order Id: "          +str(d['order_id'])+"\n"
		msg += "Symbol: *"           +str(d['symbol'])+"*\n"
		msg += "Margin: "            +str(d['margin'])+"\n"
		msg += "Leverage: "          +str(d['leverage'])+"\n"
		msg += "Direction: "         +str(d['direction'])+"\n"
		msg += "Entry Price: "       +str(d['entry_price'])+"\n"
		msg += "Exit Price: "        +str(d['entry_price'])+"\n"
		msg += "Profit Loss: "       +str(d['profit_loss'])+"\n"
		msg += "Profit Loss %: "     +str(d['profit_loss_percent'])+"\n"
		msg += "Value: "             +str(d['value'])+"\n"
		msg += "Stop Loss: "         +str(d['stop_loss'])+"\n"
		msg += "Take Profit: "       +str(d['take_profit'])+"\n"
		msg += "Shared: "            +str(d['shared'])+"\n"
		msg += "Copy of: "           +str(d['copy_of'])+"\n"
		msg += "Date Created: "      +str(d['date_created'])+"\n"
		msg += "Date Closed: "       +str(d['date_closed'])+"\n"
		msg += "`----------------`\n"

	bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 



@wprestricted.restricted
def onebroker_marketcategories(bot, update):

	# Logging
	wplogging.logger.info("/onebroker_marketcategories - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Request
	url     = "https://1broker.com/api/v2/market/categories.php?token="+config.BROKER_API_TOKEN+"&pretty=1"
	request = requests.get(url).json()

	# API Error 
	if request['error'] == True:
		msg = 'Error fetching position history, log: '+str(request['error_code'])+", Description: "+request['error_message']

		wplogging.logger.info(update.message.chat.first_name+" "+msg)
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

		return 

	# Return MSG
	resp = request['response']
	# No open orders ? 
	if len(resp) == 0:
		bot.sendMessage(chat_id=update.message.chat.id,text="No market categories returned ",parse_mode="Markdown",disable_web_page_preview=1) 
		return 

	# Build the message of open orders
	msg  = ''
	for d in resp:
		msg += d+"\n"

	bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 



@wprestricted.restricted
def onebroker_marketlist(bot, update):

	# Logging
	wplogging.logger.info("/onebroker_marketlist - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Parser setup
	parser = argparse.ArgumentParser(description='Parse position input')
	parser.add_argument('-category', type=str, required=True)

	help_msg  = "*/onebroker_marketlist [args]* [example](https://1broker.com/?c=en/content/api-documentation#market-list) \n"
	help_msg += "`-category=\"xxx\"` (str) \n"  

	# Split the arguments passed to it
	split = update.message.text.split(' ', 1)

	# Got no arguments passed to it
	if len(split) == 1:
		wplogging.logger.info("No arguments passed")
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return


	# We have arguments passed
	# Parse them
	try:
		
		# Log 
		wplogging.logger.info("Trying to parse args: "+update.message.text) 

		# Parse
		args = parser.parse_args(shlex.split(split[1]))

		# Request
		url     = "https://1broker.com/api/v2/market/list.php?token="+config.BROKER_API_TOKEN+"&pretty=1&category="+str(args.category)
		request = requests.get(url).json()

		# API Error 
		if request['error'] == True:
			msg = 'Error fetching market list, log: '+str(request['error_code'])+", Description: "+request['error_message']

			wplogging.logger.info(update.message.chat.first_name+" "+msg)
			bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

			return 

		# Return MSG
		resp = request['response']
		# No open orders ? 
		if len(resp) == 0:
			bot.sendMessage(chat_id=update.message.chat.id,text="No listed market for specified categories ",parse_mode="Markdown",disable_web_page_preview=1) 
			return 

		# Build the message of open orders
		msg  = '*Tickers for '+args.category+"*\n"
		for d in resp:
			msg += "`"+d['symbol']+"`\n"

		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 



	except SystemExit:
		wplogging.logger.info("Failed to parse args: "+update.message.text)
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return



@wprestricted.restricted
def onebroker_marketdetails(bot, update):

	# Logging
	wplogging.logger.info("/marketdetails - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Parser setup
	parser = argparse.ArgumentParser(description='Parse position input')
	parser.add_argument('-symbol', type=str, required=True)

	help_msg  = "*/marketdetails [args]* [example](https://1broker.com/?c=en/content/api-documentation#market-details) \n"
	help_msg += "`-symbol=\"xxx\"` (str) \n"  

	# Split the arguments passed to it
	split = update.message.text.split(' ', 1)

	# Got no arguments passed to it
	if len(split) == 1:
		wplogging.logger.info("No arguments passed")
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return


	# We have arguments passed
	# Parse them
	try:
		
		# Log 
		logger.info("Trying to parse args: "+update.message.text) 

		# Parse
		args = parser.parse_args(shlex.split(split[1]))


		# Request
		url     = "https://1broker.com/api/v2/market/details.php?token="+config.BROKER_API_TOKEN+"&pretty=1&symbol="+str(args.symbol)
		request = requests.get(url).json()

		# API Error 
		if request['error'] == True:
			msg = 'Error fetching market details, log: '+str(request['error_code'])+", Description: "+request['error_message']

			wplogging.logger.info(update.message.chat.first_name+" "+msg)
			bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

			return 

		# Return MSG
		resp = request['response']
		# No open orders ? 
		if len(resp) == 0:
			bot.sendMessage(chat_id=update.message.chat.id,text="No details available for inputted smybol ",parse_mode="Markdown",disable_web_page_preview=1) 
			return 

		# Build the message of open orders
		msg  = '*Details for '+str(args.symbol)+"*\n"
		msg += "Symbol: `"+str(resp['symbol'])+"`\n"
		msg += "Name: "+str(resp['name'])+"\n"
		msg += "Description: "+str(resp['description'])+"\n"
		msg += "Category: "+str(resp['category'])+"\n"
		msg += "Type: "+str(resp['type'])+"\n"
		msg += "Maximum Leverage: "+str(resp['maximum_leverage'])+"\n"
		msg += "Maximum Amount: "+str(resp['maximum_amount'])+"\n"
		msg += "Overnight charge long %: "+str(resp['overnight_charge_long_percent'])+"\n"
		msg += "Overnight charge short %: "+str(resp['overnight_charge_short_percent'])+"\n"
		msg += "Decimals: "+str(resp['decimals'])+"\n"

		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 



	except SystemExit:
		wplogging.logger.info("Failed to parse args: "+update.message.text)
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return
