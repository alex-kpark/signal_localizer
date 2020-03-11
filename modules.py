from access_points import get_scanner #use python library access_points
import pickle
import subprocess
import pandas as pd
from io import StringIO
import requests
import time 
import os

#from subprocess import Popen, PIPE


def rssi_with_access_point(target_ap_name):
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

    #print('>> Access Points')
    #print(ap_container)

    # if there does NOT EXIST a target SSID
    if target_ap_name not in ap_container:
        print('Target AP is not found!')
        return 0 #insert 0 if it does not exist

    else:
        #print('Access Point RSSI is: ', ap_container[target_ap_name])
        return int(ap_container[target_ap_name])


'''
Collect RSSI with linux commands
'''
def rssi_with_netwmanager(target_ap_name):
    
    # Get the Result from Terminal command, return in bytes
    result = subprocess.run(['nmcli', '-t', 'device', 'wifi', 'list'], stdout=subprocess.PIPE)
    
    # Transform byte result into unicode
    filtered = result.stdout.decode('utf-8')
    
    temp_num= filtered.count(':') # 1) As a single line has 7 ':'s per a ssid, we collect the number of : and
    ssid_num = int(temp_num / 7)  # 2) divide with 7 returns the number of ssids

    filtered_io = StringIO(filtered) # Read the terminal log with StringIO

    rssi_container = {}

    # By iterating each ssids
    for i in range(ssid_num):
        element = filtered_io.readline() # Read the value
    
        elem_list = element.split(':') # Make a string sequence into the list
        
        # Extract required data
        ssid = elem_list[1] # SSID
        channel = elem_list[3] # Channel info
        ssid_with_channel = ssid + '_' + channel # SSID with channel info as key to the dict
        rssi = int(elem_list[5])

        rssi_container[ssid_with_channel] = rssi # Ignored the duplicate result
    
    ssid_keys = list(rssi_container.keys()) # list of keys

    result = {key: value for key, value in rssi_container.items() if target_ap_name in key}

    if len(result) == 0:
        print('Target AP is not found!')
        return 0

    else:
        max_rssi  = int(max([i for i in result.values()])) # Maximum value of RSSI
        #print('Network Manager RSSI is: ', str(max_rssi))
        return max_rssi


'''
Collect RSSI with probing - Receive Beacon Frame around the device
'''
def rssi_with_beaconf(target_ap_name, sudo_pw):

    temp_cmd = '"SSID: ' + target_ap_name + '$"'

    #wifi chip for the xavier
    try:
        command = 'sudo iw wlan0 scan | grep "SSID: ' + target_ap_name + '$" -B6'
    
    #wifi chip in onpremise linux setting
    except Exception as e:
        command = 'sudo iw wlp0s20f3 scan | grep "SSID: ' + target_ap_name + '$" -B6'

    result = subprocess.run([command, sudo_pw], shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
    
    filtered = result.replace('\t','')
    filtered = filtered.replace(' ','')
    
    line_splitted = filtered.splitlines()
    
    index_list = [idx for idx, s in enumerate(line_splitted) if 'SSID' in s]
    
    # Final container to take all RSSI information from beacon frames
    info_container = []
    
    for idx in range(len(index_list)):
        if idx == 0: # First SSID object
            value_in_list = line_splitted[: index_list[idx]+1]

        else: # Other SSID object
            value_in_list = line_splitted[index_list[idx-1]+1 : index_list[idx]+1]

        # Process key, value in the list to the dict
        container_dict = {}
        for info in value_in_list:
            
            # Necessary information absolutely contains :
            if ':' in info:
                temp_splitted = info.split(':')
            
                key = temp_splitted[0]
                value = temp_splitted[1]

                # Preprocessing for convenient data use
                if key == 'signal':
                    value = float(value[:-3]) # drop dBm

                elif key == 'freq':
                    value = float(value)                    

                elif key == 'beaconinterval':
                    value = float(value[:-3]) # drop TUs

                # Insert the value into the key
                container_dict[key] = value 

            # Drop Misc infos (i.e. --, -, etc)            
            else:
                pass

        info_container.append(container_dict)

    temp_rssi_list = []
    for info in info_container:
        rssi = info['signal']
        temp_rssi_list.append(rssi)

    if len(temp_rssi_list) == 0:
        print('Target AP is not Found!')
        return 0

    else:
        max_rssi = max(temp_rssi_list) # RSSI represented in dBm
        #print('Beacon Frame RSSI is: ', str(max_rssi))
        return max_rssi
