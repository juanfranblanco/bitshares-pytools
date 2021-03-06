## This is a very simple asset agnostic bot based on the Market Maker bot for
## BitSharesX. This takes logic started by "toast" and massaged by Riverhead
## and xeroc.
##  
## IT IS HIGHLY RECOMMENDED YOU SETUP A BOT WALLET/ACCOUNT WITH LIMITED FUNDS. IF YOU RUN THIS AGAINST YOUR PRIMARY WALLET REALLY "BAD THINGS" COULD HAPPEN.
## 
## The purpose of this bot is: 1) Create a simple bot as a base to create more complex bots 2) Generate traffic in the bitAsset:BTSX market
## 
## SETUP:
## 
## Modify the config.json to reference your own RPC configutarion.
## Fund your bot account with at least 501 BTSX
## create a logs directory in the same directory as the python source

class MarketSpeculator():
    def __init__(self, client, exchanges, bot_config, log):
        self.log               = log
        self.client            = client
        self.config            = bot_config
        self.name              = self.config["account_name"]
        self.quote_symbol      = bot_config["asset_pair"][0]
        self.base_symbol       = bot_config["asset_pair"][1]
        self.min_base_balance  = self.config["min_base_balance"]
        self.min_quote_balance = self.config["min_quote_balance"]
        self.spread            = self.config["spread_percent"]
        self.beat_bid_by       = self.config["beat_bid_by"]
        self.beat_ask_by       = self.config["beat_ask_by"]

        self.last_bid = 0
        self.last_ask = 0

    def execute(self):
        self.log.debug("Executing bot:  %s" % self.name)

        # Some variavles
        SPREAD          = self.spread
        BEAT_BID_BY     = self.beat_bid_by
        BEAT_ASK_BY     = self.beat_ask_by
        base_precision  = self.client.get_precision(self.base_symbol)
        quote_precision = self.client.get_precision(self.quote_symbol)

        median          = self.client.get_median(self.quote_symbol)

        #Get the ratio of the last filled order
        last_price = self.client.get_last_fill(self.base_symbol, self.quote_symbol)
        last_price = last_price * (base_precision / quote_precision)

        #Get the ratio of the lowest ask price
        lowest_ask  = self.client.get_lowest_ask(self.quote_symbol, self.base_symbol)
        lowest_ask  = lowest_ask * (base_precision / quote_precision)

        #Get the ratio of the lowest ask price
        highest_bid  = self.client.get_lowest_bid(self.quote_symbol, self.base_symbol)
        highest_bid  = highest_bid * (base_precision / quote_precision)

        quote_balance = self.client.get_balance(self.name, self.quote_symbol) 
        base_balance = self.client.get_balance(self.name, self.base_symbol) 

        print( "median: %.8f" % median )
        print( "lowest ask: %.8f ( median%+.3f%% )" % (lowest_ask, (lowest_ask-median)/median*100) )
        print( "higest bid: %.8f ( median%+.3f%% )" % (highest_bid, (highest_bid-median)/median*100) )

        # The market has moved?
        canceled = []
        if ((abs(self.last_ask - last_price) / last_price) > (SPREAD / 3)) and self.last_ask != 0 :
           result = self.client.get_all_orders(self.name, self.base_symbol, self.quote_symbol)
           canceled.extend( result[0] )

        if ((abs(self.last_bid - last_price) / last_price) > (SPREAD / 3)) and self.last_bid != 0 :
           result = self.client.get_all_orders(self.name, self.base_symbol, self.quote_symbol)
           canceled.extend( result[0] )

        if ( len( canceled ) ) > 0 :
           trx = self.client.request("wallet_market_batch_update", [canceled, [], True]).json()
           self.client.wait_for_block() 

        # bid just above the highest ask
        if quote_balance > self.min_quote_balance:
           self.log.info("submitting bid for %f" % (highest_bid * (1-(BEAT_ASK_BY*2))))
           #self.client.submit_bid(self.name, ((quote_balance-self.min_quote_balance) / (highest_bid *(1-(BEAT_ASK_BY*2)))), self.base_symbol, highest_bid * (1-(BEAT_ASK_BY*2)) , self.quote_symbol)
           self.last_bid = highest_bid * (1-BEAT_BID_BY*2)
           self.last_ask = 0

        # For selling we just want to sell a few Larimers less to make sure we're the cheapest
        if base_balance > self.min_base_balance:
           self.log.info("submitting ask for %f" %  (lowest_ask * (1-(BEAT_ASK_BY))))
           #self.client.submit_ask(self.name, base_balance-self.min_base_balance, self.base_symbol, lowest_ask * (1-BEAT_ASK_BY), self.quote_symbol)
           self.last_ask = lowest_ask * (1-BEAT_ASK_BY)
           self.last_bid = 0

