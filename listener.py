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
from handlers.gwstreamer import GWStreamer
from handlers.emails import EmailBot
from handlers.slack import SlackBot
from test_hexes.mock_bayestar_event import makeBayestarMock
import datetime

allowedModes = ["test","all","test g","test x","test u","test r","test v"]

def elapsedTimeString(start):
    elapsed = int(time.time() - start)
    return "{}h {:02d}m {:02d}s".format(elapsed//(60*60), elapsed//60%60, elapsed%60)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--mode',
                        default='all',
                        help='Chose a `mode` for listen to gcn alerts. ' +\
                        'Default mode is `all`, which will include gamma ray (g), x-ray (x), UV (u), radio (r), and neutrino events (v).' +\
                        'For offline testing of all modes, use `test` mode. ' +\
                        'For offline testing of one mode, use `test P`, where `P` is one of the chars associated with a different messenger'
                        choices=['all', 'test', 'observation'])

    args = parser.parse_args()
    mode = args.mode
    start_time = time.time()
    print("Listener Activating")
    print('Running Listener in {} mode...'.format(mode), flush=True)
    
    gw_streamer = GWStreamer(mode=mode)
    email_bot = EmailBot(mode=mode)
    slack_bot = SlackBot(mode=mode)

    with open('configs/gcn_credentials.yaml', 'r', encoding='utf-8') as f:
        gcn = yaml.load(f, Loader=SafeLoader)
        slack_bot.post_message("","Starting `listener.py` for auxiliary injector")

    if mode == 'test':
        print('Reading test event...')
        """
        The below is leftover from the original main injector script
        As different modes are developed, the below will have to be modified


        fake_alert_list = glob.glob('/data/des70.a/data/desgw/O4/Main-Injector-O4b/OUTPUT/TESTING/MS240413p/UPDATE/MS240413p.json')
        print('Passing event to Handler - Listener took '+elapsedTimeString(start_time), flush=True)
        for fake_alert in fake_alert_list:
            with open(fake_alert, 'r', encoding='utf-8') as f:
                gcn_fake_alert = json.load(f)
            # slack_bot.post_message("","Starting handler on test event: {}".format(gcn_fake_alert['superevent_id']))
            gw_streamer.handle(gcn_fake_alert)
        """

    	
    elif mode.startswith('test'):
        testModes = mode.split(" ")[1] # These are the modes that are to be started for testing
        
        """
        Below is leftover from Main-injector


        print('Simulating BAYESTAR event...', flush=True)
        fake_alert = makeBayestarMock()
        with open(fake_alert, 'r', encoding='utf-8') as f:
            gcn_fake_alert = json.load(f)

        print('Passing event to Handler - Listener took '+elapsedTimeString(start_time), flush=True)
        # slack_bot.post_message("","Starting handler on mock-bayestar event: {}".format(gcn_fake_alert['superevent_id']))
        gw_streamer = GWStreamer(mode='mock')
        gw_streamer.handle(gcn_fake_alert)
        """
        	
    elif mode=='all':
        try:
            consumer = Consumer(client_id=gcn['client_id'],
                                client_secret=gcn['client_secret'])
            consumer.subscribe(['igwn.gwalert'])

            today = datetime.date.today().day
            init_day = 1
            
            while True:
                for message in consumer.consume(timeout=10):
                    print('Trigger Received...')
                    gcn_alert = json.loads(message.value())
                    print('Passing event to Handler.', flush=True)
                    gw_streamer.handle(gcn_alert)
                
                if datetime.date.today().day != today:
                    slack_bot.post_message("","`listener.py` has been running nonstop in {} mode for {} days".format(mode, init_day))
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
            print("Mode not supported. Supplied mode: {}. Allowed modes are {}.".format(mode,allowedModes)) 
