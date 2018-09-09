# Napoleon Bitcoin/Crypto telegram   
*bot by [@whalepoolbtc](https://t.me/whalepoolbtc) - [https://whalepool.io](https://whalepool.io)*   

This  bot allows you to view your balance, place orders etc on various bitcoin/crypto exchanges from telegram.   
  
Currently supported exchanges:   
- [Bitmex](http://bitmex.whalepool.io)  
- 1[Broker](http://1broker.whalepool.io)  
  

### Install
```bash
git clone https://github.com/Whalepool/Napoleon.git napoleon  
pip install -r requirements.txt
```     

### Setup config
`cp config.sample.yaml config.yaml`  
  
### Run
`python3.6 napoleon.py`  
  

For more info join [@whalepoolbtc](https://t.me/whalepoolbtc) on telegram   

![Profile pic](napoleon.jpg)    
------ 


  
## General commands
| Command | Action | 
| --- | --- | 
| **User** | | 
| /id | get your telegram userid | 
| /debug | output telegram bot variables to console |   
  
# 1Broker commands   
| Command | Action | 
| --- | --- | 
| /onebroker\_gettxlog | last 10 transactions  |
| /onebroker\_getbalances | summary of balances  |
| /onebroker\_getpositions | summary of positions  |
| **Orders** | |
| /onebroker\_openorders | list open orders  |
| /onebroker\_createposition | open a long/short [args]  |
| /onebroker\_cancelorder | cancel an order  |
| **Position** | |
| /onebroker\_openpositions | list open positions  |
| /onebroker\_editposition | edit a position [args]  |
| /onebroker\_closeposition | close a position [args]  |
| /onebroker\_cancelcloseposition | cancel a position trying to close [args]  |
| /onebroker\_positionhistory | historic positions sorted by closing date  |
| **Market** |  |
| /onebroker\_marketcategories | list market categories  |
| /onebroker\_marketlist | list markets for category [args]  |
| /onebroker\_marketdetails | details of the market [args]  |  

# Bitmex commands    
| Command | Action | 
| --- | --- | 
| /bitmex\_fullorder | make full order [args]  | 
| /bitmex\_order | make order [args]  | 
| /bitmex\_getbalance | get bitmex account balance  | 
| /bitmex\_listorders | get bitmex open order list  | 
| /bitmex\_positionlist | get bitmex open position list  | 
| /bitmex\_cancelorders | cancel all open bitmex orders for a symbol  | 
| /bitmex\_cancelorder | cancel one open bitmex order, give orderID  | 
| /bitmex\_tradehistory | get bitmex last 5 executions  | 