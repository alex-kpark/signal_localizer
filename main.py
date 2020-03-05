from access_points import get_scanner #use python library access_points
import pickle
import threading#, schedule
from time import ctime
import time

'''
1. Get RSS values in a particular period
'''

def get_rssi_val(target_ap_name):
    '''
    >> Input
    - target_ap_name(str): SSID pf target ap (i.e. darpa_subt_cellphone)

    >> Output
    - rssi_val: None (if there's no matching SSID) or int value of RSSI

    '''
    wifi_scanner = get_scanner() # Make an object (scanner) to scan
    ap_results = wifi_scanner.get_access_points() #list

    ap_container = {} # SSID and its quality (RSS) will be added as key, value, respectively
    
    for ap in ap_results:
        ap_container[ap.ssid] = ap.quality

    #print('>> AP Info')
    #print(ap_container)

    # if there does NOT EXIST a target SSID
    if target_ap_name not in ap_container:
        print('Target AP is not found!')
        return 0 #insert 0 if it does not exist

    # if target SSID EXISTS
    else:
        print('>> Target RSSI is: ', ap_container[target_ap_name])
        return int(ap_container[target_ap_name])

def collect(run_num):
    rssi_container = []
    sec = 0
    try:
        while True:
            print('>> Timestamp: ' + str(sec))
            sec += 1
            rssi_val = get_rssi_val('shadysideinn')
            rssi_container.append(rssi_val)
            time.sleep(1)

    except KeyboardInterrupt:
        print('Exit the Collection process!')
        print('Total RSSI data: ', str(len(rssi_container)))
        print(rssi_container)

        f = open('rssi_val_' + str(run_num) + '.pkl', 'wb')
        pickle.dump(rssi_container, f)

        #with open('rssi_val_' + str(run_num) + '.pkl', 'wb') as f:
        #    pickle.dump(rssi_container, f)

collect(1)

'''
def collect():
    timer_func = threading.Timer(3.0, collect) #set the Timer
    timer_func.start()
    rssi_val = get_rssi_val('kyungho_iphone_for_subt')
    print(ctime())
    timer_func.cancel()

collect()
'''

#get_rssi_val('shadysideinn')

    

    