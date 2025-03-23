"""
Python script to listen from non-LVK alerts trough gcn.
"""

import glob
import time
import traceback
import json
from argparse import ArgumentParser
import yaml
from yaml.loader import SafeLoader
from gcn_kafka import Consumer
from handlers.streamer import alertStreamer
from handlers.emails import EmailBot
from handlers.slack import SlackBot
import datetime
from tests import testHandler

allowedModes = ["test","all","test g","test x","test v"]
allowedChars = ["g","x","v"]

# Gamma ray: Einstein probe  gcn.notices.einstein_probe.wxt.alert
# X ray: Swift gcn.notices.swift.bat.guano
# Radio (r): No great option, yet
# Neutrino: IceCube : gcn.notices.icecube.lvk_nu_track_search

subscriptionDict = {
                    "g":"gcn.notices.einstein_probe.wxt.alert",
                    "x":"gcn.notices.swift.bat.guano",
                    "v":"gcn.notices.icecube.lvk_nu_track_search"
                    }

# Other sources to consider: SuperNova Early Warning System (SNEWS)

def elapsedTimeString(start):
    elapsed = int(time.time() - start)
    return "{}h {:02d}m {:02d}s".format(elapsed//(60*60), elapsed//60%60, elapsed%60)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--mode',
                        default='all',
                        help='Chose a `mode` for listen to gcn alerts. ' +\
                        'Default mode is `all`, which will include gamma ray (g), x-ray (x), and neutrino events (v).' +\
                        'For offline testing of all modes, use `test` mode. ' +\
                        'For offline testing of one mode, use `test P`, where `P` is one of the chars associated with a different messenger'
                        choices=allowedModes)

    args = parser.parse_args()
    mode = args.mode
    start_time = time.time()
    print("Listener Activating")
    print('Running Listener in {} mode...'.format(mode), flush=True)
    
    alert_streamer = alertStreamer(mode=mode)
    email_bot = EmailBot(mode=mode)
    slack_bot = SlackBot(mode=mode)

    with open('configs/gcn_credentials.yaml', 'r', encoding='utf-8') as f:
        gcn = yaml.load(f, Loader=SafeLoader)
        slack_bot.post_message("","Starting `listener.py` for auxiliary injector")

    if mode == 'test':
        print('Reading test events...')
        for character in allowedChars:
            postString = "Starting test handler for mode {}".format(character)
            slack_bot.post_message("",postString)
            print(postString)
            testHandler(character)
            	
    elif mode.startswith('test'):
        testModes = list(mode.split(" ")[1]) # These are the modes that are to be started for testing, all chars
        
        for mode in testModes:
            postString = "Starting test handler for mode {}".format(mode)
            slack_bot.post_message("",postString)
            print(postString)
            testHandler(mode)

       	
    elif mode=='all':
        try:
            consumer = Consumer(client_id=gcn['client_id'],
                                client_secret=gcn['client_secret'])
            # initial
            for value in subscriptionDict.values(): 
                consumer.subscribe([value])

            today = datetime.date.today().day
            init_day = 1
            
            while True:
                for message in consumer.consume(timeout=10):
                    print('Trigger Received...')
                    gcn_alert = json.loads(message.value())
                    print('Passing event to Handler.', flush=True)
                    alertStreamer.handle(gcn_alert)
                
                if datetime.date.today().day != today:
                    slack_bot.post_message("","`listener.py` for `Auxiliary-Injector` has been running nonstop in {} mode for {} days".format(mode, init_day))
                    today = datetime.date.today().day
                    init_day +=1

        except Exception as e:
            print(e)
            slack_bot.post_message("","Listener went down! Please investigate! Traceback attached <@U05V24X6MHB><@U0545QECWJZ><@UAV5VNB9N>. {}".format(traceback.format_exc()))
            email_bot.send_email(subject='Listener went down, see traceback',
                                text=traceback.format_exc(),
                                emergency=True)
    else:
        raise ValueError:
            print("Mode not supported.\nSupplied mode: {}.\nAllowed modes are {}.".format(mode,allowedModes)) 
