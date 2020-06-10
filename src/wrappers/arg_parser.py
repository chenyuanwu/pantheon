import argparse
import sys

def parse_wrapper_args(run_first, **keywords):
    if run_first != 'receiver' and run_first != 'sender':
        sys.exit('Specify "receiver" or "sender" to run first')

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='option')

    subparsers.add_parser(
        'deps', help='print a space-separated list of build dependencies')
    subparsers.add_parser(
        'run_first', help='print which side (sender or receiver) runs first')
    subparsers.add_parser(
        'setup', help='set up the scheme (required to be run at the first '
        'time; must make persistent changes across reboots)')
    subparsers.add_parser(
        'setup_after_reboot', help='set up the scheme (required to be run '
        'every time after reboot)')

    receiver_parser = subparsers.add_parser('receiver', help='run receiver')
    sender_parser = subparsers.add_parser('sender', help='run sender')

    http_server_parser = subparsers.add_parser('http_server', help='run http server')
    http_client_parser = subparsers.add_parser('http_client', help='run http client')

    if keywords.get('http_reversed', None):
        http_client_parser.add_argument('port', help='port for http cilent to listen on')
        http_server_parser.add_argument('ip', metavar='IP', help='IP address of http client')
        http_server_parser.add_argument('port', help='port of http client')
    else:
        http_server_parser.add_argument('port', help='port for http server to listen on')
        http_client_parser.add_argument('ip', metavar='IP', help='IP address of http server')
        http_client_parser.add_argument('port', help='port of http server')

    if run_first == 'receiver':
        receiver_parser.add_argument('port', help='port to listen on')
        sender_parser.add_argument(
            'ip', metavar='IP', help='IP address of receiver')
        sender_parser.add_argument('port', help='port of receiver')
    else:
        sender_parser.add_argument('port', help='port to listen on')
        receiver_parser.add_argument(
            'ip', metavar='IP', help='IP address of sender')
        receiver_parser.add_argument('port', help='port of sender')

    args = parser.parse_args()

    if args.option == 'run_first':
        print run_first

    return args


def receiver_first(**keywords):
    return parse_wrapper_args('receiver', **keywords)


def sender_first(**keywords):
    return parse_wrapper_args('sender', **keywords)
