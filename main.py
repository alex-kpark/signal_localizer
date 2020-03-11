from modules import *

import pickle
import time
import argparse


'''
>> Set the clock and collect data
'''
parser = argparse.ArgumentParser(description='Using Argparser')
parser.add_argument('--venue', required=True, help='The venue of Run')
parser.add_argument('--run', required=True, help='The number of Run')
parser.add_argument('--ssid_name', required=True, help='Target AP name')
parser.add_argument('--pw', required=True, help='password for sudo code execution')

args = parser.parse_args()

run = args.run
ssid_name = args.ssid_name
sudo_pw = args.pw
venue = args.venue

print(type(run), run)
print(type(ssid_name), ssid_name)
print(type(sudo_pw), sudo_pw)
print(type(venue), venue)

def collect(run_num, ssid_name):
    rssi_container_acp = []
    rssi_container_netw = []
    rssi_container_beaconf = []

    sec = 0
    try:
        while True:
            print('>> Timestamp: ' + str(sec))
            sec += 1
            rssi_val_from_acp = rssi_with_access_point(ssid_name) #from access point
            rssi_val_from_netw = rssi_with_netwmanager(ssid_name) #from command (nmcli - network manager)
            rssi_val_from_beaconf = rssi_with_beaconf(ssid_name, sudo_pw) #from probing beacon frame

            rssi_container_acp.append(rssi_val_from_acp)
            rssi_container_netw.append(rssi_val_from_netw)
            rssi_container_beaconf.append(rssi_val_from_beaconf)
            
            print('> Access P: ', rssi_container_acp)
            print('> Network M: ', rssi_container_netw)
            print('> Beacon F: ', rssi_container_beaconf)

            time.sleep(1)

    except KeyboardInterrupt:
        print('Exit the Collection process!')

        total_container = {}
        total_container['rssi_acp'] = rssi_container_acp
        total_container['rssi_netw'] = rssi_container_netw
        total_container['rssi_beaconf'] = rssi_container_beaconf

        f = open(venue + '_rssi_val_' + str(run_num) + '.pkl', 'wb')
        pickle.dump(total_container, f)
        f.close()

        #with open('rssi_val_' + str(run_num) + '.pkl', 'wb') as f:
        #    pickle.dump(rssi_container, f)

collect(run, ssid_name)

