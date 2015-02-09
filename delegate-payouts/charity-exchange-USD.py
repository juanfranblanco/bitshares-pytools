#!/usr/bin/python
import bitsharesrpc
import config

accountname = "payouts.charity"
percentage  = 0.90

if __name__ == "__main__":
 rpc = bitsharesrpc.client(config.url, config.user, config.passwd)
 #print rpc.info()
 print rpc.wallet_open(config.wallet)
 print rpc.unlock(100, config.unlock)

 ## Get Price
 #price = float((rpc.marketstatus("USD","BTSX"))[ "result" ][ "avg_price_1h" ])
 orders = rpc.blockchain_market_order_book( "USD", "BTS", 1 )
 for o in orders[ "result" ] :
  if o[ 0 ][ "type" ] == "ask_order" :
   price = float(o[ 0 ][ "market_index" ][ "order_price" ][ "ratio" ]) * 10

 #prices = []
 #for o in (rpc.orderhistory("USD","BTSX",10))[ "result" ]:
 # prices.append(float(o[ "bid_price" ][ "ratio" ])*10)
 # prices.append(float(o[ "ask_price" ][ "ratio" ])*10)
 #price = sum( prices ) / len( prices );
 #print price

 ## getbalance
 balances = rpc.getbalance(accountname)
 for b in (balances)[ "result" ][ 0 ][ 1 ] :
   if b[ 0 ] == 0 :
       balance = float(b[ 1 ])/1.0e5;

## put bid order 
quant = balance * percentage
print "wallet_market_submit_ask %s %f %s %f %s\n\n" %(accountname,  quant, "BTSX", price, "USD")
#print rpc.wallet_market_submit_ask(accountname, quant, "BTSX", price, "USD")