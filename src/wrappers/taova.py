#!/usr/bin/env python

import os
from os import path
from subprocess import check_call
from multiprocessing import Process
import context
from helpers import utils

import arg_parser
import sys
import traceback
import signal

def recvfrom(receiver, filename):
    f = open(filename, 'w+')
    f.close()
    while True:
        # pay attention to the type conversions,
        s = receiver.recvfrom()
        with open(filename, 'a+') as f:
            f.write(s)

def main():
    args = arg_parser.receiver_first()

    cc_repo = path.join(context.third_party_dir, 'genericCC')
    recv_src = path.join(cc_repo, 'receiver')
    send_src = path.join(cc_repo, 'sender')

    if args.option == 'deps':
        print ('makepp libboost-dev libprotobuf-dev protobuf-c-compiler '
               'protobuf-compiler libjemalloc-dev libboost-python-dev')
        return

    if args.option == 'setup':
        check_call(['makepp'], cwd=cc_repo)
        return

    if args.option == 'receiver':
        cmd = [recv_src, args.port]
        check_call(cmd)
        return

    if args.option == 'sender':
        rat_file = path.join(cc_repo, 'RemyCC-2014-100x.dna')
        sh_cmd = (
            'export MIN_RTT=1000000 && %s serverip=%s serverport=%s if=%s '
            'offduration=1 onduration=1000000 traffic_params=deterministic,'
            'num_cycles=1' % (send_src, args.ip, args.port, rat_file))
        check_call(sh_cmd, shell=True)
        return

    if args.option == 'http_client':
        sys.path.append(cc_repo)
        rat_file = path.join(cc_repo, 'RemyCC-2014-100x.dna')
        import pygenericcc
        sender = pygenericcc.REMYSender(rat_file, args.ip, int(args.port), 0)
        with open(os.path.join(cc_repo, 'index.html'), 'r') as f:
            line = f.read()
            print line
            # pay attention to the type conversions between python and c++
            sender.send(line, len(line), 1)

    if args.option == 'http_server':
        sys.path.append(cc_repo)
        import pygenericcc

        receiver = pygenericcc.Receiver(int(args.port))
        filename = os.path.join(utils.tmp_dir, 'remy_index.html')
        try:
            p = Process(target=recvfrom, args=(receiver, filename))
            p.start()
            p.join()
        except:
            print traceback.format_exc()
            utils.kill_proc_group(p, signal.SIGTERM)



if __name__ == '__main__':
    main()
