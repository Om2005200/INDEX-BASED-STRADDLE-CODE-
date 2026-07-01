
import requests as rq
import pandas as pd
import csv 
import json 
from datetime import datetime
import time 
import os 
import upstox_client



class NIFTY_STRADDLE:
    def __init__(self):
        self.live_ltp=None
        self.access_token=''
        self.ltp_data = {}
        self.streamer = None
        self.websocket_connected = False
    def ensure_order_log(self):
        if not os.path.exists("nifty_order_log.json"):
            with open("nifty_order_log.json", "w") as f:
                json.dump([], f)
    def saving_the_order_log(self,data):
        with open('nifty_order_log.json','w') as x:
            data=json.dump(data,x,indent=4)
        return data
    

    def opening_the_order_log(self):
        try:
            with open('nifty_order_log.json','r') as order:
                data=json.load(order)
                return data
        except FileNotFoundError:
            print('No file found ')
        return []
    

    def getting_the_options_contract(self):
        api_endpoint='https://api.upstox.com/v2/option/contract?instrument_key=NSE_INDEX|Nifty 50&expiry_date=2026-06-02'
        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(self.access_token)

        }
        response=rq.get(api_endpoint,headers=headers)
        print(response.status_code)
        data=response.json()
        print(data)
        with open('nifty_revised_options_chain.json','w') as g:
            json.dump(data,g,indent=4)
        return data
    def openinig_the_data(self):


        try:
            with open('nifty_revised_options_chain.json','r') as v:
                data = json.load(v)
                return data

        except FileNotFoundError:
            print("Options chain file not found")
            return None
        
            
    # def main(self,token: str):

    #     live_ltp = None

    #     configuration = upstox_client.Configuration()

    #     configuration.access_token = self.access_token

    #     streamer = upstox_client.MarketDataStreamerV3(
    #         upstox_client.ApiClient(configuration)
    #     )

    #     def on_open():

    #         streamer.subscribe(
    #             ["BSE_FO|{}".format(token)],
    #             "full"
    #         )

    #     def on_message(message):

    #         nonlocal live_ltp

    #         try:

    #             if 'feeds' not in message:
    #                 return

    #             feeds = message['feeds']

    #             for keys, values in feeds.items():

    #                 live_ltp = values['fullFeed']['marketFF']['ltpc']['cp']

    #                 streamer.disconnect()

    #         except Exception as e:

    #             print(e)

    #     streamer.on("open", on_open)

    #     streamer.on("message", on_message)

    #     streamer.connect()

    #     while live_ltp is None:
    #         time.sleep(0.1)

    #     return live_ltp
    def start_websocket(self, tokens):


        configuration = upstox_client.Configuration()
        configuration.access_token = self.access_token

        self.streamer = upstox_client.MarketDataStreamerV3(
            upstox_client.ApiClient(configuration)
        )

        def on_open():

            self.websocket_connected = True

            print("Websocket Connected")

            self.streamer.subscribe(
                tokens,
                "full"
            )

        def on_message(message):

            try:

                feeds = message.get("feeds", {})

                for token, values in feeds.items():

                    #ltp = values['fullFeed']['marketFF']['ltpc']['cp']
                    ltp = (
                        values['fullFeed']['marketFF']['ltpc'].get('ltp')
                        or
                        values['fullFeed']['marketFF']['ltpc'].get('cp')
                    )

                    self.ltp_data[token] = ltp
                    #print(token,ltp)

            except Exception as e:

                print("Websocket Error:", e)

        def on_error(error):

            print("Websocket Error:", error)

        def on_close():

            self.websocket_connected = False

            print("Websocket Closed")

        self.streamer.on("open", on_open)
        self.streamer.on("message", on_message)
        self.streamer.on("error", on_error)
        self.streamer.on("close", on_close)

        self.streamer.connect()

    def get_ltp(self, exchange_token):


        token = f"NSE_FO|{exchange_token}"

        return self.ltp_data.get(token)
    def taking_a_call_position(self):
        order_placing_api='https://api-hft.upstox.com/v3/order/place'
        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(self.access_token)
        }
        position_time='09:25'
        current_time=datetime.now().strftime('%H:%M')
        if current_time>=position_time:
            order_log=self.opening_the_order_log() or []
            for orders in order_log:
                past_order_instrument_type=orders['instrument_type']
                past_order_status=orders['status']
                if past_order_instrument_type=='CE' :
                    return 
                
            main_data=self.openinig_the_data()
            ltp_set=[]
            required_premium_set=[]
            whole_data=main_data['data']
            master_instrument_type = None
            for datas in whole_data:
                name=datas['name']
                expiry=datas['expiry']
                exchange_token=datas['exchange_token']
                trading_symbol=datas['trading_symbol']
                strike_price=datas['strike_price']
                instrument_type=datas['instrument_type']
                if instrument_type=='CE':
                    master_name=name
                    master_expiry=expiry
                    main_instrument_type=instrument_type
                    master_exchange_token=exchange_token
                    master_trading_symbol=trading_symbol
                    master_strike_price=strike_price
                    #ltp = self.get_ltp(f"NSE_FO|{master_exchange_token}")
                    ltp = self.get_ltp(master_exchange_token)
                    if ltp is None:
                        continue

                    required_ltp=55
                    if ltp not in ltp_set:
                        ltp_set.append(ltp)
                        for prices in ltp_set:
                            cost=prices
                            if cost>=required_ltp and cost<56:
                                trade_token=master_exchange_token
                                trade_symbol=master_trading_symbol
                                trade_strikeprice=master_strike_price
                                trade_expiry=expiry
                                trade_instrument_type=main_instrument_type
                                quantity=195
                                order_ltp=cost
                                lots=3
                                new_order={
                                    'quantity':quantity,
                                    'product':'D',
                                    'validity':'DAY',
                                    'price':0,
                                    'tag':'string',
                                    'instrument_token':'NSE_FO|{}'.format(master_exchange_token),
                                    'order_type':'MARKET',
                                    'transaction_type':'SELL',
                                    'disclosed_quantity':0,
                                    'trigger_price':0,
                                    'is_amo':False,
                                    'slice':False
                                }
                                order_history=[{
                                    'quantity':quantity,
                                    'product':'D',
                                    'validity':'DAY',
                                    'price':0,
                                    'tag':'string',
                                    'instrument_token':'NSE_FO|{}'.format(master_exchange_token),
                                    'order_type':'MARKET',
                                    'transaction_type':'SELL',
                                    'disclosed_quantity':0,
                                    'trigger_price':0,
                                    'is_amo':False,
                                    'slice':False,
                                    'market_protection':0,
                                    'ltp':cost,
                                    'trade_token':trade_token,
                                    'trade_symbol':trade_symbol,
                                    'trade_strikeprice':trade_strikeprice,
                                    'trade_expiry':trade_expiry,
                                    'entry_price':cost,
                                    'status':'OPEN',
                                    'instrument_type':trade_instrument_type

                                }]
                               
                                try:

                                    request=rq.post(order_placing_api,json=new_order,headers=headers)
                                    print('STATUS:',request.status_code)
                                    print('BODY:',request.text)
                                except Exception as e:
                                    print('Order fialed exiting the function {}'.format(e))
                                    return
                                
                                old_orders = self.opening_the_order_log() or []
                                old_orders=list(old_orders)
                                #old_orders.append(order_history)

                                old_orders.extend(order_history)
                                with open('nifty_order_log.json','w') as j:
                                    json.dump(old_orders,j,indent=4)
                                return 
                            elif cost>required_ltp:
                                trade_token=master_exchange_token
                                trade_symbol=master_trading_symbol
                                trade_strikeprice=master_strike_price
                                master_instrument_type=main_instrument_type
                                trade_expiry=expiry
                                pre=cost
                                required_premium_set.append({
                                    'ltp':pre,
                                    'trade_token':master_exchange_token,
                                    'trade_symbol':master_trading_symbol,
                                    'trade_strikeprice':master_strike_price,
                                    #'trade_expiry':master_strike_price,
                                    'trade_expiry':expiry
                                })   
            if not required_premium_set:
                return     
            suffix=min(required_premium_set,key=lambda x:x['ltp'])
            order_token=suffix['trade_token']
            trade_symbol=suffix['trade_symbol']
            trade_strikeprice=suffix['trade_strikeprice']
            trade_expiry=suffix['trade_expiry']
            lot_quantity=195
            lots=5
            low_instrument_type=master_instrument_type
            new_order={
                'quantity':lot_quantity,
                'product':'D',
                'validity':'DAY',
                'price':0,
                'tag':'string',
                'instrument_token':'NSE_FO|{}'.format(order_token),
                'order_type':'MARKET',
                'transaction_type':'SELL',
                'disclosed_quantity':0,
                'trigger_price':0,
                'is_amo':False,
                'slice':False

            }
            order_history=[{
                'quantity':lot_quantity,
                'product':'D',
                'validity':'DAY',
                'price':0,
                'tag':'string',
                'instrument_token':'NSE_FO|{}'.format(order_token),
                'order_type':'MARKET',
                'transaction_type':'SELL',
                'disclosed_quantity':0,
                'trigger_price':0,
                'is_amo':False,
                'slice':False,
                'market_protection':0,
                'ltp':suffix['ltp'],
                'trade_token':order_token,
                'trade_symbol':trade_symbol,
                'trade_strikeprice':trade_strikeprice,
                'trade_expiry':trade_expiry,
                'entry_price':suffix['ltp'],
                'status':'OPEN',
                'instrument_type':low_instrument_type
                            
            }]
            try:

                requests=rq.post(order_placing_api,json=new_order,headers=headers)
                print(requests.status_code)
                print(requests.text)
            except Exception as e:
                print('An error ocurred exiting the code {}'.format(e))
                return
            

            print(order_history)
            old_orders = self.opening_the_order_log() or []
            old_orders=list(old_orders)


            old_orders.extend(order_history)
            with open('nifty_order_log.json','w') as t:
                json.dump(old_orders,t,indent=4)




    
    def taking_a_put_position(self):
        order_placing_api='https://api-hft.upstox.com/v3/order/place'
        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(self.access_token)
        }
        position_time='09:25'
        current_time=datetime.now().strftime('%H:%M')
        if current_time>=position_time:
            order_log=self.opening_the_order_log() or []
            for orders in order_log:
                past_order_instrument_type=orders['instrument_type']
                past_order_status=orders['status']
                if past_order_instrument_type=='PE' :
                    return 
                
            main_data=self.openinig_the_data()
            ltp_set=[]
            required_premium_set=[]
            whole_data=main_data['data']
            master_instrument_type = None
            for datas in whole_data:
                name=datas['name']
                expiry=datas['expiry']
                exchange_token=datas['exchange_token']
                trading_symbol=datas['trading_symbol']
                strike_price=datas['strike_price']
                instrument_type=datas['instrument_type']
                if instrument_type=='PE':
                    master_name=name
                    master_expiry=expiry
                    main_instrument_type=instrument_type
                    master_exchange_token=exchange_token
                    master_trading_symbol=trading_symbol
                    master_strike_price=strike_price
                    ltp = self.get_ltp(master_exchange_token)
                    if ltp is None:
                        continue

                    required_ltp=55
                    if ltp not in ltp_set:
                        ltp_set.append(ltp)
                        for prices in ltp_set:
                            cost=prices
                            if cost>=required_ltp and cost<56:
                                trade_token=master_exchange_token
                                trade_symbol=master_trading_symbol
                                trade_strikeprice=master_strike_price
                                trade_expiry=expiry
                                trade_instrument_type=main_instrument_type
                                quantity=195
                                order_ltp=cost
                                lots=3
                                new_order={
                                    'quantity':quantity,
                                    'product':'D',
                                    'validity':'DAY',
                                    'price':0,
                                    'tag':'string',
                                    'instrument_token':'NSE_FO|{}'.format(master_exchange_token),
                                    'order_type':'MARKET',
                                    'transaction_type':'SELL',
                                    'disclosed_quantity':0,
                                    'trigger_price':0,
                                    'is_amo':False,
                                    'slice':False
                                }
                                order_history=[{
                                    'quantity':quantity,
                                    'product':'D',
                                    'validity':'DAY',
                                    'price':0,
                                    'tag':'string',
                                    'instrument_token':'NSE_FO|{}'.format(master_exchange_token),
                                    'order_type':'MARKET',
                                    'transaction_type':'SELL',
                                    'disclosed_quantity':0,
                                    'trigger_price':0,
                                    'is_amo':False,
                                    'slice':False,
                                    'market_protection':0,
                                    'ltp':cost,
                                    'trade_token':trade_token,
                                    'trade_symbol':trade_symbol,
                                    'trade_strikeprice':trade_strikeprice,
                                    'trade_expiry':trade_expiry,
                                    'entry_price':cost,
                                    'status':'OPEN',
                                    'instrument_type':trade_instrument_type

                                }]
                                try:
                                    request=rq.post(order_placing_api,json=new_order,headers=headers)
                                    print(request.status_code)
                                    print(request.text)
                                except Exception as e:
                                    print('An error ocurred {}'.format(e))
                                    
                                old_orders=self.opening_the_order_log() or []
                                old_orders=list(old_orders)
                                old_orders.extend(order_history)
                                with open('nifty_order_log.json','w') as j:
                                    json.dump(old_orders,j,indent=4)
                                return 
                            elif cost>required_ltp:
                                trade_token=master_exchange_token
                                trade_symbol=master_trading_symbol
                                trade_strikeprice=master_strike_price
                                master_instrument_type=main_instrument_type
                                trade_expiry=expiry
                                pre=cost
                                required_premium_set.append({
                                    'ltp':pre,
                                    'trade_token':master_exchange_token,
                                    'trade_symbol':master_trading_symbol,
                                    'trade_strikeprice':master_strike_price,
                                    #'trade_expiry':master_strike_price,
                                    'trade_expiry':expiry
                                })        
            # if not required_premium_set:
            #     return
            suffix=min(required_premium_set,key=lambda x:x['ltp'])
            order_token=suffix['trade_token']
            trade_symbol=suffix['trade_symbol']
            trade_strikeprice=suffix['trade_strikeprice']
            trade_expiry=suffix['trade_expiry']
            lot_quantity=195
            lots=5
            low_instrument_type=main_instrument_type
            new_order={
                'quantity':lot_quantity,
                'product':'D',
                'validity':'DAY',
                'price':0,
                'tag':'string',
                'instrument_token':'NSE_FO|{}'.format(order_token),
                'order_type':'MARKET',
                'transaction_type':'SELL',
                'disclosed_quantity':0,
                'trigger_price':0,
                'is_amo':False,
                'slice':False
            }
            order_history=[{
                'quantity':lot_quantity,
                'product':'D',
                'validity':'DAY',
                'price':0,
                'tag':'string',
                'instrument_token':'NSE_FO|{}'.format(order_token),
                'order_type':'MARKET',
                'transaction_type':'SELL',
                'disclosed_quantity':0,
                'trigger_price':0,
                'is_amo':False,
                'slice':False,
                'market_protection':0,
                'ltp':suffix['ltp'],
                'trade_token':order_token,
                'trade_symbol':trade_symbol,
                'trade_strikeprice':trade_strikeprice,
                'trade_expiry':trade_expiry,
                'entry_price':suffix['ltp'],
                'status':'OPEN',
                'instrument_type':low_instrument_type
                            
            }]
            try:
                requests=rq.post(order_placing_api,json=new_order,headers=headers)
                print(requests.status_code)
            except Exception as e:
                print('An erro ocurred {}'.format(e))

            print(order_history)
            old_orders=self.opening_the_order_log() or []
            old_orders=list(old_orders)
            old_orders.extend(order_history)
            with open('nifty_order_log.json','w') as t:
                json.dump(old_orders,t,indent=4)



    def exiting_the_trades(self):
            
        # main_data=self.opening_the_order_log()
        # for orders in main_data:
        #     product=orders['product']
        #     trading_token=orders['trade_token']
        #     entry_price=orders['entry_price']
        #     ltp=self.main(trading_token)
        #     stop_loss_level=1.25
        #     stop_loss=entry_price*stop_loss_level
        #     order_status=orders['status']

        #     if ltp>=stop_loss and order_status=='OPEN':
        #         instrument_token=orders['instrument_token']
        #         quantity=orders['quantity']
        #         trade_symbol=orders['trade_symbol']
        #         orders['status']='CLOSED'

        #         break

        #     elif ltp<stop_loss and order_status=='OPEN':
        #         continue
        #     elif ltp>=stop_loss and order_status=='CLOSED':
        #         continue
        main_data=self.opening_the_order_log() or []
        url='https://api-hft.upstox.com/v3/order/place'
          
        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(self.access_token)
        }

        for orders in main_data:
            instrument_type=orders['instrument_type']
            #exchange_token=orders['exchange_token']
            status=orders['status']
            entry_price=orders['entry_price']
            quantity=orders['quantity']
            token=orders['instrument_token']
            stop_loss_level=1.25
            main_sl=entry_price*stop_loss_level
            ltp=self.ltp_data.get(token)
            if ltp is None:

                #ltp=self.ltp_data.get(f"NSE_FO|{token.split('|')[-1]}")
                ltp = self.ltp_data.get(token)
            if instrument_type=='CE' and status=='OPEN':
                current_ltp=ltp

                if current_ltp>=main_sl:
                    new_order={
                        'quantity':quantity,
                        'product':'D',
                        'validity':'DAY',
                        'price':0,
                        'tag':'string',
                        'instrument_token':token,
                        'order_type':'MARKET',
                        'transaction_type':'BUY',
                        'disclosed_quantity':0,
                        'trigger_price':0,
                        'is_amo':False,
                        'slice':False,
                        'market_protection':0

                    }
                    orders['status']='CLOSED'
                    with open('nifty_order_log.json','w') as k:
                        json.dump(main_data,k,indent=4)
                        


                    try:

                        request=rq.post(url,json=new_order,headers=headers)
                        print(request.status_code)
                    except Exception as e:
                        print('Án error ocuureree while placin g the order {}'.format(e))
                    return
                
            elif instrument_type=='PE' and status=='OPEN':
                current_ltp=ltp
                if current_ltp>=main_sl:



                    new_order={
                        'quantity':quantity,
                        'product':'D',
                        'validity':'DAY',
                        'price':0,
                        'tag':'string',
                        'instrument_token':token,
                        'order_type':'MARKET',
                        'transaction_type':'BUY',
                        'disclosed_quantity':0,
                        'trigger_price':0,
                        'is_amo':False,
                        'slice':False,


                    }
                    orders['status']='CLOSED'
                    with open('nifty_order_log.json','w') as f:
                        json.dump(main_data,f,indent=4)
                        


                    try:
                        request=rq.post(url,json=new_order,headers=headers)
                        print(request.status_code)
                    except Exception as e:
                        print('An error ocurred {}'.format(e))
                    return
nifty=NIFTY_STRADDLE()           
nifty.ensure_order_log() 
options_data=nifty.getting_the_options_contract()
main_data = nifty.openinig_the_data()


tokens = []

for item in main_data['data']:

    tokens.append(
        f"NSE_FO|{item['exchange_token']}"
    )

nifty.start_websocket(tokens)

time.sleep(5)
while True:

    if not nifty.websocket_connected:

        try:

            if nifty.streamer:

                try:
                    nifty.streamer.disconnect()
                except:
                    pass

            nifty.start_websocket(tokens)

            time.sleep(5)

        except Exception as e:

            print(e)

    nifty.taking_a_call_position()

    nifty.taking_a_put_position()

    nifty.exiting_the_trades()

    time.sleep(1)

