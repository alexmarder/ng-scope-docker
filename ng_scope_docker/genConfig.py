#!/usr/bin/python3

import subprocess
import sys
from argparse import ArgumentParser

from libconf import dumps, LibconfInt64
from ng_scope_docker.arfcn_calc import earfcn2freq

class USRPException(Exception):
    pass
  

cfg_tpl = {
    'nof_rf_dev': 1, # Number of antennas
    'disable_plot': False,
    'remote_enable': True, # Streaming functionality
    'decode_single_ue': False,
    'rnti': 9185, # single UE decoding
    # RF Config
    'dci_log_config': {
        'lod_dl': True,
        'log_ul': True
    }
}

rf_cfg_tpl = {
    'rf_freq': LibconfInt64(2127500000),
    'N_id_2': -1, 
    'rf_args': 'serial=3272344',
    'nof_thread': 3,
    'disable_plot': True,
    'log_dl': True,
    'log_ul': True,
}

def parse_usrp_output(output):
    usrps = []
    for line in output.splitlines():
        if 'serial' in line:
            no_spaces = ''.join(line.split())
            usrps.append(no_spaces.split(':')[1])
    return usrps


def get_usrps():
    try:
        output = subprocess.check_output('uhd_find_devices', shell=True).strip().decode()
    except subprocess.CalledProcessError as e:
        output = ''
    return parse_usrp_output(output)

def gen_rf_config(earfcn, usrpID):
    tmp = rf_cfg_tpl.copy()
    freq = earfcn2freq(earfcn)
    if freq is None:
        print('Invalid EARFCN {0}'.format(earfcn))
        exit(1)
    tmp['rf_freq'] = int(freq*1000000)
    tmp['rf_args'] = 'serial={0}'.format(usrpID)
    
    return tmp

def gen_config(rfNum, earfcns):
    cfg_tpl['nof_rf_dev'] = rfNum
    
    usrps = get_usrps()
    if len(usrps) < rfNum:
        raise USRPException('ERROR: Not enough available USRPs (avail: {0}, req: {1})'.format(len(usrps), rfNum))
    
    # Populate main structure
    cfg_tpl['nof_rf_dev'] = rfNum
    
    # Add RFs
    for i in range(rfNum):
        cfg_tpl['rf_config{0}'.format(i)] = gen_rf_config(earfcns, usrps[i])

    return cfg_tpl

def safe_config(cfg, output):
    # Generate file
    out = dumps(cfg)
    # Convert booleans into lowercase
    out = out.replace('True', 'true').replace('False', 'false')

    with open(output, 'w') as f:
        f.write(out)

def main():
    parser = ArgumentParser()
    parser.add_argument('-r', '--rf-number', type=int)
    parser.add_argument('-e', '--earfcn', type=int)
    parser.add_argument('-o', '--output')
    args = parser.parse_args()

    try:
        cfg = gen_config(args.rf_number, args.earfcn)
    except USRPException as e:
        print(e)
        sys.exit(1)

    safe_config(cfg, args.output)

if __name__ == '__main__':
    main()
