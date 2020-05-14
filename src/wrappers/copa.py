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

def recvfrom(receiver, f):
    while True:
        # pay attention to the type conversions,
        s = receiver.recvfrom()
        print s
        f.write(s)

def main(delta_conf):
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
        sh_cmd = (
            'export MIN_RTT=1000000 && %s serverip=%s serverport=%s '
            'offduration=1 onduration=1000000 traffic_params=deterministic,'
            'num_cycles=1 cctype=markovian delta_conf=%s'
            % (send_src, args.ip, args.port, delta_conf))

        with open(os.devnull, 'w') as devnull:
            # suppress debugging output to stdout
            check_call(sh_cmd, shell=True, stdout=devnull)
        return

    if args.option == 'http_client':
        sys.path.append(cc_repo)
        import pygenericcc
        sender = pygenericcc.COPASender(args.ip, int(args.port), 0)
        with open(os.path.join(cc_repo, 'index.html'), 'r') as f:
            for line in f:
                # pay attention to the type conversions between python and c++
                sender.send(line, len(line), 1)

    if args.option == 'http_server':
        sys.path.append(cc_repo)
        import pygenericcc

        receiver = pygenericcc.Receiver(int(args.port))
        filename = os.path.join(utils.tmp_dir, 'copa_index.html')
        try:
            f = open(filename, 'w')
            p = Process(target=recvfrom, args=(receiver, f))
            p.start()
            p.join()
        except:
            print traceback.format_exc()
            utils.kill_proc_group(p, signal.SIGKILL)
            f.close()
        finally:
            f.close()



if __name__ == '__main__':
    main('do_ss:auto:0.1')
