#!/usr/bin/env python

from subprocess import check_call

import arg_parser
import context
from helpers import kernel_ctl, utils
import sys
import signal
import os
import urllib
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(os.path.join(context.third_party_dir, 'proto-quic', 'www.example.org', 'index.html'), 'r') as f:
                for line in f:
                    self.wfile.write(line)
        else:
            self.send_error(404)


def setup_bbr():
    # load tcp_bbr kernel module (only available since Linux Kernel 4.9)
    kernel_ctl.load_kernel_module('tcp_bbr')

    # add bbr to kernel-allowed congestion control list
    kernel_ctl.enable_congestion_control('bbr')

    # check if qdisc is fq
    kernel_ctl.check_qdisc('fq')


def main():
    args = arg_parser.receiver_first()

    if args.option == 'deps':
        print 'iperf'
        return

    if args.option == 'setup_after_reboot':
        setup_bbr()
        return

    if args.option == 'receiver':
        cmd = ['iperf', '-Z', 'bbr', '-s', '-p', args.port]
        check_call(cmd)
        return

    if args.option == 'sender':
        cmd = ['iperf', '-Z', 'bbr', '-c', args.ip, '-p', args.port,
               '-t', '75']
        check_call(cmd)
        return

    if args.option == 'http_server':
        cur_cc = kernel_ctl.get_congestion_control()
        kernel_ctl.set_congestion_control('bbr')
        server = HTTPServer(('localhost', int(args.port)), HTTPRequestHandler)

        def stop_signal_handler(signum, frame):
            server.server_close()
            sys.stderr.write("HTTP Server Stops: caught signal %s\n" % signum)
            kernel_ctl.set_congestion_control(cur_cc)

        signal.signal(signal.SIGTERM, stop_signal_handler)
        signal.signal(signal.SIGINT, stop_signal_handler)
        sys.stderr.write("HTTP Server Starts\n")
        server.serve_forever()


    if args.option == 'http_client':
        cur_cc = kernel_ctl.get_congestion_control()
        kernel_ctl.set_congestion_control('bbr')
        url = 'http://%s:%s/' % (args.ip, int(args.port))
        filename = os.path.join(utils.tmp_dir, 'index.html')
        if os.path.isfile(filename):
            os.remove(filename)
        try:
            urllib.urlretrieve(url, filename)
            sys.stderr.write("File transfer succeed\n")
        finally:
            kernel_ctl.set_congestion_control(cur_cc)


if __name__ == '__main__':
    main()
