#BitMEX affiliate account commands
#
#Command list:
#
# - bitmex_order - makes order with args: symbol, qty, orderprice, stoploss (opt)
# - bitmex_cancelorders - cancels all orders (all symbols, for now...)
# - bitmex_listorders - lists open orders
# - bitmex_positionlist - lists open positions
# 
#

#deps

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



#this is just quick function to govern leverage before any order actions are taken
def bitmex_leveragepolice(symbol):
	verb    =  "POST"
	nonce   =  str(int(time.time()))
	path    =  "/api/v1/position/leverage"
	data      = '{"symbol":"'+str(symbol)+'","leverage":3}'
	wplogging.logger.info("swapcheck "+data)
	message =  verb + path + nonce + data
	signature = hmac.new(bytes(config.SHITMEX_API_SECRET, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()
	req = urllib.request.Request('https://www.bitmex.com'+path)
	req.add_header('api-nonce', nonce)
	req.add_header('api-key', config.SHITMEX_API_KEY)
	req.add_header('api-signature', signature)
	req.add_header('Content-Type', 'application/json')
	datab=str.encode(data) #Bytes needed for POST data
	
	try:
		resp = urllib.request.urlopen(req, datab)
	except urllib.request.HTTPError as err:

		msg = 'HTTP Error: '+str(err.code)

		wplogging.logger.info("Leverage Police failed: "+msg)
		#bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

		return


	content     = resp.read()
	decodeddata =json.loads(content.decode())
	time.sleep(1)

@wprestricted.restricted
def bitmex_cancelorder(bot, update):

        # Logging
	wplogging.logger.info("/bitmexcancelorder - "+update.message.from_user.username)

        # Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)


        # Parser setup
	parser = argparse.ArgumentParser(description='Parse order cancellation input')
	parser.add_argument('-orderid', type=str, required=True)


	help_msg  = "*/bitmex_cancelorder [args]* \n"
	help_msg += "`-orderid=\"xxx\"` (str) \n" 
        
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


		verb    =  "DELETE"
		nonce   =  str(int(time.time()))
		path    =  "/api/v1/order"
		data    = '{"orderID":"'+str(args.orderid)+'"}'

		message =  verb + path + nonce + data

                #gen sig
		signature = hmac.new(bytes(config.SHITMEX_API_SECRET, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()

                #build GET req headers
		req = urllib.request.Request('https://www.bitmex.com'+path)
		req.add_header('api-nonce', nonce)
		req.add_header('api-key', config.SHITMEX_API_KEY)
		req.add_header('api-signature', signature)
		req.add_header('Content-Type', 'application/json')
		req.get_method = lambda: 'DELETE'
		datab=str.encode(data) #Bytes needed for POST data

		try:
			resp = urllib.request.urlopen(req, datab)

		except urllib.request.URLError as e:
			msg = 'URL Error: '+str(e.reason)
			wplogging.logger.info(update.message.chat.first_name+" "+msg)
			bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

			return


		except urllib.request.HTTPError as err:

			msg = 'HTTP Error: '+str(err.code)

			wplogging.logger.info(update.message.chat.first_name+" "+msg)
			bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

			return


		content     = resp.read()
		decodeddata =json.loads(content.decode())

		msg = config.MSG_HEADER_BITMEX
		msg += "Order Cancelled"

		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

	except SystemExit:
		wplogging.logger.info("Failed to parse args: "+update.message.text)
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return



@wprestricted.restricted
def bitmex_cancelorders(bot, update):

	# Logging
	wplogging.logger.info("/bitmexcancelorders - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)


	# Parser setup
	parser = argparse.ArgumentParser(description='Parse order cancellation input')
	parser.add_argument('-symbol', type=str, required=True)


	help_msg  = "*/bitmex_cancelorders [args]* \n"
	help_msg += "`-symbol=\"xxx\"` _optional_ (str) \n" 
	help_msg += "This cancels all open orders for the specified symbol\n"
	help_msg += "To cancel all symbols orders, use symbol=all"
	
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


		verb    =  "DELETE"
		nonce   =  str(int(time.time()))
		path    =  "/api/v1/order/all"
		data = ''
		if args.symbol != "all":
			data    = '{"symbol":"'+str(args.symbol)+'"}'

		message =  verb + path + nonce + data

		#gen sig
		signature = hmac.new(bytes(config.SHITMEX_API_SECRET, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()

		#build GET req headers
		req = urllib.request.Request('https://www.bitmex.com'+path)
		req.add_header('api-nonce', nonce)
		req.add_header('api-key', config.SHITMEX_API_KEY)
		req.add_header('api-signature', signature)
		req.add_header('Content-Type', 'application/json')
		req.get_method = lambda: 'DELETE'
		datab=str.encode(data) #Bytes needed for POST data
		
		try:
			resp = urllib.request.urlopen(req, datab)
		except urllib.request.HTTPError as err:

			msg = 'HTTP Error: '+str(err.reason)

			wplogging.logger.info(update.message.chat.first_name+" "+msg)
			bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

			return


		content     = resp.read()
		decodeddata =json.loads(content.decode())

		
		msg = config.MSG_HEADER_BITMEX
		msg += "All "+str(args.symbol)+" orders cancelled"

		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

	except SystemExit:
		wplogging.logger.info("Failed to parse args: "+update.message.text)
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return

@wprestricted.restricted
def bitmex_tradehistory(bot, update):

        # Logging   
	wplogging.logger.info("/bitmex_tradehistory - "+update.message.from_user.username)

        # Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	verb    =  "GET"
	nonce   =  str(int(time.time()))
	path    =  "/api/v1/execution/tradeHistory?count=5&reverse=true"
	data    = ''

	message =  verb + path + nonce + data   

        #gen sig
	signature = hmac.new(bytes(config.SHITMEX_API_SECRET, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()

        #build GET req headers
	req = urllib.request.Request('https://www.bitmex.com'+path)
	req.add_header('api-nonce', nonce)
	req.add_header('api-key', config.SHITMEX_API_KEY)
	req.add_header('api-signature', signature)
	req.add_header('Content-Type', 'application/json')
        
	try:
		resp = urllib.request.urlopen(req)

	except urllib.request.HTTPError as err:

		msg = 'HTTP Error: '+str(err.code)

		wplogging.logger.info(update.message.chat.first_name+" "+msg)
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1)

		return

	content     = resp.read()
	decodeddata =json.loads(content.decode())

# No open orders ? 
	if len(decodeddata) == 0:
		msg = config.MSG_HEADER_BITMEX
		msg += "Currently no open orders"
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1)
		return 

        # Build+send messages of open orders

	for d in decodeddata:
		msg = config.MSG_HEADER_BITMEX
		msg += "Order Id: "+str(d['orderID'])+"\n"
		msg += "Symbol: "+str(d['symbol'])+"\n"
		msg += "Side: "+str(d['side'])+"\n"
		msg += "Quantity (Contracts): "+str(d['orderQty'])+"\n"
		msg += "Order Type: "+str(d['ordType'])+"\n"
		msg += "Order Price: "+str(d['price'])+"\n"
		if (str(d['stopPx']) != "None"):
			msg += "Stop Trigger: "+str(d['stopPx'])+"\n"
		msg += "Extra flags: "+str(d['execInst'])+"\n"
		msg += "Avg price: "+str(d['avgPx'])+"\n"
		msg += "Status: "+str(d['ordStatus'])+"\n"
		msg += "Quantity remaining: "+str(d['leavesQty'])+"\n"
		msg += "Date Created: "+str(d['timestamp'])+"\n"
		msg += "`----------------`\n"
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1)



@wprestricted.restricted
def bitmex_listorders(bot, update):

	# Logging
	wplogging.logger.info("/bitmexlistorders - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	verb    =  "GET"
	nonce   =  str(int(time.time()))
	path    =  "/api/v1/order?filter=%7B%22open%22%3A%20true%7D"
	data    = ''

	message =  verb + path + nonce + data

	#gen sig
	signature = hmac.new(bytes(config.SHITMEX_API_SECRET, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()

	#build GET req headers
	req = urllib.request.Request('https://www.bitmex.com'+path)
	req.add_header('api-nonce', nonce)
	req.add_header('api-key', config.SHITMEX_API_KEY)
	req.add_header('api-signature', signature)
	req.add_header('Content-Type', 'application/json')
	
	try:
		resp = urllib.request.urlopen(req)

	except urllib.request.HTTPError as err:

		msg = 'HTTP Error: '+str(err.code)

		wplogging.logger.info(update.message.chat.first_name+" "+msg)
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

		return

	content     = resp.read()
	decodeddata =json.loads(content.decode())

# No open orders ? 
	if len(decodeddata) == 0:
		msg = config.MSG_HEADER_BITMEX
		msg += "Currently no open orders"
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 
		return 

	# Build+send messages of open orders

	for d in decodeddata:
		msg = config.MSG_HEADER_BITMEX
		msg += "Order Id: "+str(d['orderID'])+"\n"
		msg += "Symbol: "+str(d['symbol'])+"\n"
		msg += "Side: "+str(d['side'])+"\n"
		msg += "Quantity (Contracts): "+str(d['orderQty'])+"\n"
		msg += "Order Type: "+str(d['ordType'])+"\n"
		msg += "Order Price: "+str(d['price'])+"\n"
		if (str(d['stopPx']) != "None"):
			msg += "Stop Trigger: "+str(d['stopPx'])+"\n"
		msg += "Trailing Stop Value: "+str(d['pegOffsetValue'])+"\n"
		msg += "Extra flags: "+str(d['execInst'])+"\n"
		msg += "Quantity remaining: "+str(d['leavesQty'])+"\n"
		msg += "Date Created: "+str(d['timestamp'])+"\n"
		msg += "`----------------`\n"
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

@wprestricted.restricted
def bitmex_positionlist(bot, update):

	# Logging
	wplogging.logger.info("/bitmexpositionlist - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	verb    =  "GET"
	nonce   =  str(int(time.time()))
	path    =  "/api/v1/position?filter=%7B%22isOpen%22%3A%20true%7D"
	data    = ''

	message =  verb + path + nonce + data

	#gen sig
	signature = hmac.new(bytes(config.SHITMEX_API_SECRET, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()

	#build req headers
	req = urllib.request.Request('https://www.bitmex.com'+path)
	req.add_header('api-nonce', nonce)
	req.add_header('api-key', config.SHITMEX_API_KEY)
	req.add_header('api-signature', signature)
	req.add_header('Content-Type', 'application/json')

	try:
		resp = urllib.request.urlopen(req)
	except urllib.request.HTTPError as err:

		msg = 'HTTP Error: '+str(err.code)

		wplogging.logger.info(update.message.chat.first_name+" "+msg)
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

		return


	content     = resp.read()
	decodeddata =json.loads(content.decode())


	# No open positions ? 
	if len(decodeddata) == 0:
		msg = config.MSG_HEADER_BITMEX
		msg += "Currently no open positions" 
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 
		return 

	# Build+send messages of open orders

	for d in decodeddata:
		msg = config.MSG_HEADER_BITMEX
		msg += "Symbol: "+str(d['symbol'])+"\n"
		msg += "Quantity: "+str(d['currentQty'])+" Contracts\n"
		msg += "Entry Price: "+str(d['avgEntryPrice'])+" \n"
		msg += "Current Price: "+str(d['markPrice'])+" \n"
		msg += "Order Value: "+str(abs(d['posCost']/100000000))+" BTC\n"
		msg += "PNL(%): "+str(round(d['unrealisedPnlPcnt']*100,2))+"% \n"
		msg += "Margin: "+str(d['posMargin']/100000000)+" BTC\n"
		msg += "PNL: "+str(d['unrealisedPnl']/100000000)+" BTC\n"
		msg += "ROE: "+str(round(d['unrealisedRoePcnt']*100,2))+"%\n"
		msg += "Date Created: "+str(d['timestamp'])+"\n"
		msg += "`----------------`\n"
		if d['posMargin']>0:
			bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

@wprestricted.restricted
def bitmex_getbalance(bot, update):

	# Logging
	wplogging.logger.info("/bitmexbalance - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	verb    =  "GET"
	nonce   =  str(int(time.time()))
	path    =  "/api/v1/user/margin"
	data    =  ""
	message =  verb + path + nonce + data

	#gen sig
	signature = hmac.new(bytes(config.SHITMEX_API_SECRET, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()

	#build req headers
	req = urllib.request.Request('https://www.bitmex.com/api/v1/user/margin')
	req.add_header('api-nonce', nonce)
	req.add_header('api-key', config.SHITMEX_API_KEY)
	req.add_header('api-signature', signature)

	try:
		resp        = urllib.request.urlopen(req)
	except urllib.request.HTTPError as err:

		msg = 'HTTP Error: '+str(err.code)

		wplogging.logger.info(update.message.chat.first_name+" "+msg)
		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

		return

	content     = resp.read()
	decodeddata =json.loads(content.decode())

	#vars of interest
	#This is the affiliate account balance in satoshi
	currbalance  = str(decodeddata['walletBalance']/100000000)
	currord      = str(decodeddata['initMargin']/100000000)
	currpos      = str(decodeddata['marginBalance']/100000000)
	curravail    = str(decodeddata['availableMargin']/100000000)

	# Reply 
	msg = config.MSG_HEADER_BITMEX
	msg += "Current wallet balance: "+currbalance+"\n"
	msg += "Current balance net of positions: "+currpos+"\n"
	msg += "Current order value: "+currord+"\n"
	msg += "Available margin: "+curravail+"\n"

	bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

@wprestricted.restricted        
def bitmex_fullorder(bot, update):

        # Logging
	wplogging.logger.info("/bitmex_order - "+update.message.from_user.username)

        # Lreciept confirmation 
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

        # Parser setup
	parser = argparse.ArgumentParser(description='Parse order input')

	parser.add_argument('-symbol', type=str, required=True)
	parser.add_argument('-qty', type=int, help='Quantity - number of contracts, to short/sell make negative', required=True)
	parser.add_argument('-limitprice', type=float, help='Price to put limit order.', required=True)
	parser.add_argument('-stoptrigger', type=float, help='Stop trigger price.', required=True)
	parser.add_argument('-stoplimit', type=float, help='Stop execution order price.', required=True)
	parser.add_argument('-takeprofit', type=float, help='Take Profit Trigger (market exec).', required=True)
	parser.add_argument('-trailing', type=str)
	help_msg  = "*/bitmex_fullorder [args]* [example](https://www.bitmex.com/api/explorer/#!/Order/Order_new) \n"
	help_msg += "`-symbol=\"xxx\"` (str) \n" 
	help_msg += "`-qty=\"10000\"` (int) \n" 
	help_msg += "`-limitprice=\"1025.50\"` (float) \n" 
	help_msg += "`-stoptrigger=\"1015.21\"` (float) \n" 
	help_msg += "`-stoplimit=\"1000.21\"` (float) \n" 
	help_msg += "`-takeprofit=\"1050.21\"` (float) \n"  
	help_msg += "`-trailing=\"xxx\"` _optional_ (str) yes (autosets to stoplimit - stoptrigger) \n"
	help_msg += "\nThis is to make 3 orders: 1 limit, 1 stop/trigger for taking profit, and 1 stop/trigger for stop loss.\n"
	help_msg += "An example: you want to go long 1 contract XBTUSD at 1133, with a stoploss at 1120 and a take profit at 1150\n"
	help_msg += "`/bitmex_fullorder -symbol=\"XBTUSD\" -qty=1 -limitprice=1133 -stoptrigger=1120 -stoplimit=1100 -takeprofit=1150` \n"
	help_msg += "This will execute the 3 separate orders (this is how BitMEX works) and print the confirmations for each \n"
	help_msg += "To make this a short play instead, make the qty parameter negative.\n Note that the take profit order is a \"MarketIfTouched\"(a stop-market order) where you only specify the trigger price, while the stop loss is a \"StopLimit\" order type, where you specify trigger AND stop price execution."



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

                



		#Part 1 of full order: LIMIT ENTRY

		# Police 3x leverage for all orders!!!!!!!!!!!!!!!
		bitmex_leveragepolice(args.symbol)

		verb    =  "POST"
		nonce   =  str(int(time.time()))
		path    =  "/api/v1/order"

                # Data parms
		data      = '{"symbol":"'+args.symbol+'"'
		data      += ',"orderQty":'+str(args.qty)
		data      += ',"price":'+str(args.limitprice)
		data      += '}'

		wplogging.logger.info("request: "+data)
		message =  verb + path + nonce + data
                #gen sig
		signature = hmac.new(bytes(config.SHITMEX_API_SECRET, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()
                #build GET req headers
		req = urllib.request.Request('https://www.bitmex.com'+path)
		req.add_header('api-nonce', nonce)
		req.add_header('api-key', config.SHITMEX_API_KEY)
		req.add_header('api-signature', signature)
		req.add_header('Content-Type', 'application/json')
		datab=str.encode(data) #Bytes needed for POST data
		
		try:
			resp = urllib.request.urlopen(req, datab)
		except urllib.request.HTTPError as err:

			msg = 'HTTP Error: '+str(err.code)

			wplogging.logger.info(update.message.chat.first_name+" "+msg)
			bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

			return

		content     = resp.read()
		decodeddata =json.loads(content.decode())

                # API Error 
		if 'error' in decodeddata:
			msg = 'Error creating order, log: '+str(decodeddata['error']['name'])+", Description: "+decodeddata['error']['message']

			wplogging.logger.info(update.message.chat.first_name+" "+msg)
			bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

			return 

		msg = config.MSG_HEADER_BITMEX
                # Build the message of open orders
		msg += '*Created order #'+str(decodeddata['orderID'])+"*\n"
		msg += "Symbol: `"+str(decodeddata['symbol'])+"`\n"
		msg += "Quantity: "+str(decodeddata['orderQty'])+"\n"
		msg += "Side: "+str(decodeddata['side'])+"\n"
		msg += "Price: "+str(decodeddata['price'])+"\n"
		msg += "Order type: "+str(decodeddata['ordType'])+"\n"
		msg += "Extra flags: "+str(decodeddata['execInst'])+"\n"
		msg += "Date Created: "+str(decodeddata['timestamp'])

		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 
		
		time.sleep(1)

		#Part 2: STOP LOSS

		if args.trailing:
			trail = args.stoplimit-args.stoptrigger
		verb    =  "POST"
		nonce   =  str(int(time.time()))
		path    =  "/api/v1/order"
		oppqty=args.qty*-1
                # Data parms
		data      = '{"symbol":"'+args.symbol+'"'
		data      += ',"orderQty":'+str(oppqty)
		data      += ',"price":'+str(args.stoplimit)
		data      += ',"execInst":"Close,LastPrice"'
		data += ',"ordType":"StopLimit"'    
		data += ',"stopPx":'+str(args.stoptrigger)
		if args.trailing:
			data += ',"pegPriceType":"TrailingStopPeg"'
			data += ',"pegOffsetValue":'+str(trail)
		data      += '}'

		wplogging.logger.info("request: "+data)
		message =  verb + path + nonce + data
                #gen sig
		signature = hmac.new(bytes(config.SHITMEX_API_SECRET, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()
                #build GET req headers
		req = urllib.request.Request('https://www.bitmex.com'+path)
		req.add_header('api-nonce', nonce)
		req.add_header('api-key', config.SHITMEX_API_KEY)
		req.add_header('api-signature', signature)
		req.add_header('Content-Type', 'application/json')
		datab=str.encode(data) #Bytes needed for POST data
		
		try:
			resp = urllib.request.urlopen(req, datab)

		except urllib.request.HTTPError as err:

			msg = 'HTTP Error: '+str(err.code)

			wplogging.logger.info(update.message.chat.first_name+" "+msg)
			bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

			return


		content     = resp.read()
		decodeddata =json.loads(content.decode())

		msg = config.MSG_HEADER_BITMEX
                # Build the message of open orders
		msg += '*Created order #'+str(decodeddata['orderID'])+"*\n"
		msg += "Symbol: `"+str(decodeddata['symbol'])+"`\n"
		msg += "Quantity: "+str(decodeddata['orderQty'])+"\n"
		msg += "Side: "+str(decodeddata['side'])+"\n"
		msg += "Price: "+str(decodeddata['price'])+"\n"
		msg += "Order type: "+str(decodeddata['ordType'])+"\n"
		msg += "Stop Trigger: "+str(decodeddata['stopPx'])+"\n"
		msg += "Extra flags: "+str(decodeddata['execInst'])+"\n"
		msg += "Trailing Stop Value: "+str(decodeddata['pegOffsetValue'])+"\n"
		msg += "Date Created: "+str(decodeddata['timestamp'])

		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

		time.sleep(1)


		#Part 3: TAKE PROFIT

		verb    =  "POST"
		nonce   =  str(int(time.time()))
		path    =  "/api/v1/order"

                # Data parms
		data      = '{"symbol":"'+args.symbol+'"'
		data      += ',"orderQty":'+str(oppqty)
		data      += ',"execInst":"Close,LastPrice"'
		data      += ',"ordType":"MarketIfTouched"'    
		data      += ',"stopPx":'+str(args.takeprofit)
		data      += '}'

		wplogging.logger.info("request: "+data)
		message =  verb + path + nonce + data
                #gen sig
		signature = hmac.new(bytes(config.SHITMEX_API_SECRET, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()
                #build GET req headers
		req = urllib.request.Request('https://www.bitmex.com'+path)
		req.add_header('api-nonce', nonce)
		req.add_header('api-key', config.SHITMEX_API_KEY)
		req.add_header('api-signature', signature)
		req.add_header('Content-Type', 'application/json')
		datab=str.encode(data) #Bytes needed for POST data

		try:
			resp = urllib.request.urlopen(req, datab)

		except urllib.request.HTTPError as err:

			msg = 'HTTP Error: '+str(err.code)

			wplogging.logger.info(update.message.chat.first_name+" "+msg)
			bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

			return


		content     = resp.read()
		decodeddata =json.loads(content.decode())

		msg = config.MSG_HEADER_BITMEX

		   # Build the message of open orders
		msg += '*Created order #'+str(decodeddata['orderID'])+"*\n"
		msg += "Symbol: `"+str(decodeddata['symbol'])+"`\n"
		msg += "Quantity: "+str(decodeddata['orderQty'])+"\n"
		msg += "Side: "+str(decodeddata['side'])+"\n"
		msg += "Price: "+str(decodeddata['price'])+"\n"
		msg += "Order type: "+str(decodeddata['ordType'])+"\n"
		msg += "Stop Trigger: "+str(decodeddata['stopPx'])+"\n"
		msg += "Extra flags: "+str(decodeddata['execInst'])+"\n"
		msg += "Date Created: "+str(decodeddata['timestamp'])

		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 



	except SystemExit:
		wplogging.logger.info("Failed to parse args: "+update.message.text)
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return



@wprestricted.restricted	
def bitmex_order(bot, update):

	# Logging
	wplogging.logger.info("/bitmex_order - "+update.message.from_user.username)

	# Lreciept confirmation
	bot.sendChatAction(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

	# Parser setup
	parser = argparse.ArgumentParser(description='Parse order input')
	parser.add_argument('-symbol', type=str, required=True)
	parser.add_argument('-qty', type=int, help='Quantity - number of contracts, to short/sell make negative', required=True)
	parser.add_argument('-orderprice', type=float, help='Price to execute order.')
	parser.add_argument('-stop', type=float, help='Stop trigger price.')
	parser.add_argument('-type', type=str, help='Custom order type.')
	parser.add_argument('-extra', type=str, help='Extra Flags.')
	parser.add_argument('-trailing', type=float, help='Trail stop offset, neg for sell, pos for buy.')


	help_msg  = "*/bitmex_order [args]* [example](https://www.bitmex.com/api/explorer/#!/Order/Order_new) \n"
	help_msg += "`-symbol=\"xxx\"` (str) \n" 
	help_msg += "`-qty=\"10000\"` (int) \n" 
	help_msg += "`-orderprice=\"1020.50\"` _optional_ (float) \n" 
	help_msg += "`-stop=\"1010.21\"` _optional_ (float) \n" 
	help_msg += "`-type=\"MarketIfTouched\"` _optional_ (str) \n"
	help_msg += "`-extra=\"Close\"` _optional_ (str) \n" 
	help_msg += "`-trailing=\"-10\"` _optional_ (float) \n"
	help_msg += "This is to make a single order execution, different from /bitmex\_fullorder.\n"
	help_msg += "Example 1: making an individual takeprofit order (lets say you are long at $1001 taking profit at $1010):\n"
	help_msg += "`/bitmex_order -symbol=\"XBTUSD\" -qty=\"-100\" -stop=\"1010.21\" -type=\"MarketIfTouched\" -extra=\"Close,LastPrice`\"\n"
	help_msg += "Note: there's no orderprice since this is a market-stop order. Once last price hits 1010.21, it executes a close sell of 100 contracts.\n"
	help_msg += "Example 2: A stop loss order (let's say you're long from $1020 and want a stop triggering at $1010.21 to sell out down to $990, but have it trail -10):\n"
	help_msg += "`/bitmex_order -symbol=\"XBTUSD\" -qty=\"-100\" -stop=\"1010.21\" -orderprice=\"990\" -type=\"StopLimit\"-extra=\"Close,LastPrice\" -trailing=\"-10\"`\n"
	help_msg += "Negative quantity meanss sell. Stop is the trigger, and order price is the execution of the limit, extra ensures the order is close-only and trigger is based on Last Price\nUse BitMEX API to see more \"ordType\" choices  and possibilities for \"execInst\" on /put/order endpoint"




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

		# Police 3x leverage for all orders!!!!!!!!!!!!!!!
		bitmex_leveragepolice(args.symbol)

		verb    =  "POST"
		nonce   =  str(int(time.time()))
		path    =  "/api/v1/order"

		# Data parms
		data      = '{"symbol":"'+args.symbol+'"'
		data      += ',"orderQty":'+str(args.qty)
		if args.orderprice:
			data      += ',"price":'+str(args.orderprice)
		if args.extra:
			data      += ',"execInst":"'+args.extra+'"'
		if args.type:
			data += ',"ordType":"'+args.type+'"'    
		if args.stop:
			data += ',"stopPx":'+str(args.stop)
		if args.trailing:
			data += ',"pegPriceType":"TrailingStopPeg"'
			data += ',"pegOffsetValue":'+str(args.trailing)
		data      += '}'

		wplogging.logger.info("request: "+data)


		message =  verb + path + nonce + data

		#gen sig
		signature = hmac.new(bytes(config.SHITMEX_API_SECRET, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()

		#build GET req headers
		req = urllib.request.Request('https://www.bitmex.com'+path)
		req.add_header('api-nonce', nonce)
		req.add_header('api-key', config.SHITMEX_API_KEY)
		req.add_header('api-signature', signature)
		req.add_header('Content-Type', 'application/json')
		datab=str.encode(data) #Bytes needed for POST data
		


		try:
			resp = urllib.request.urlopen(req, datab)

		except urllib.request.HTTPError as err:

			msg = 'HTTP Error: '+str(err.code)

			wplogging.logger.info(update.message.chat.first_name+" "+msg)
			bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

			return


		content     = resp.read()
		decodeddata =json.loads(content.decode())

		msg = config.MSG_HEADER_BITMEX
		# Build the message of open orders
		msg += '*Created order #'+str(decodeddata['orderID'])+"*\n"
		msg += "Symbol: `"+str(decodeddata['symbol'])+"`\n"
		msg += "Quantity: "+str(decodeddata['orderQty'])+"\n"
		msg += "Side: "+str(decodeddata['side'])+"\n"
		msg += "Price: "+str(decodeddata['price'])+"\n"
		msg += "Order type: "+str(decodeddata['ordType'])+"\n"
		if args.stop:
			msg += "Stop Trigger: "+str(decodeddata['stopPx'])+"\n"
		if args.trailing:
			msg += "Trailing Stop Value: "+str(d['pegOffsetValue'])+"\n"
		msg += "Extra flags: "+str(decodeddata['execInst'])+"\n"
		msg += "Date Created: "+str(decodeddata['timestamp'])

		bot.sendMessage(chat_id=update.message.chat.id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

	except SystemExit:
		wplogging.logger.info("Failed to parse args: "+update.message.text)
		bot.sendMessage(chat_id=update.message.chat.id,text=help_msg,parse_mode="Markdown",disable_web_page_preview=1)
		return




