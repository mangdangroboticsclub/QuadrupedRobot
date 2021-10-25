#!/usr/bin/env python3

import sys
import argparse
import json
import time
import select
import pexpect

import UDPComms
import msgpack

def peek_func(port):
    sub = UDPComms.Subscriber(port, timeout = 10)
    while 1:
        try:
            data = sub.recv()
            print( json.dumps(data) )
        except UDPComms.timeout:
            exit()

def poke_func(port, rate):
    pub = UDPComms.Publisher(port)
    data = None

    while 1:
        if select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline()
            # detailed behaviour
            # reading from file: -ignores empty lines -repeats last line forever
            # reading from terminal: -repeats last command
            if line.rstrip():
                data = line.rstrip()
            elif len(line) == 0:
                # exit() #uncomment to quit on end of file
                pass
            else:
                continue

        if data != None:
            pub.send( json.loads(data) )
            time.sleep( rate/1000 )

def call_func(command, ssh = True):
    child = pexpect.spawn(command)

    if ssh:
        i = 1
        while i == 1:
            try:
                i = child.expect(['password:', 
                             'Are you sure you want to continue connecting', 
                                  'Welcome'], timeout=20)
            except pexpect.EOF:
                print("Can't connect to device")
                exit()
            except pexpect.TIMEOUT:
                print("Interaction with device failed")
                exit()

            if i == 1:
                child.sendline('yes')
        if i == 0:
            child.sendline('raspberry')
    else:
        try:
            child.expect('robot:', timeout=1)
            child.sendline('hello')
        except pexpect.TIMEOUT:
            pass

    child.interact()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser')

    peek = subparsers.add_parser("peek")
    peek.add_argument('port', help="UDP port to subscribe to", type=int)

    poke = subparsers.add_parser("poke")
    poke.add_argument('port', help="UDP port to publish the data to", type=int)
    poke.add_argument('rate', help="how often to republish (ms)", type=float)

    peek = subparsers.add_parser("discover")

    commands = ['status', 'log', 'start', 'stop', 'restart', 'enable', 'disable']
    for command in commands:
        status = subparsers.add_parser(command)
        status.add_argument('host', help="Which device to look for this program on")
        status.add_argument('unit', help="The unit whose status we want to know", 
                                                        nargs='?', default=None)

    connect = subparsers.add_parser('connect')
    connect.add_argument('host', help="Which device to log into")

    args = parser.parse_args()

    if args.subparser == 'peek':
        peek_func(args.port)
    elif args.subparser == 'poke':
        poke_func(args.port, args.rate)
    elif args.subparser == 'connect':
        call_func("ssh pi@"+args.host+".local")
    elif args.subparser == 'discover':
        call_func("nmap -sP 10.0.0.0/24", ssh=False)

    elif args.subparser in commands:
        if args.unit is None:
            args.unit = args.host

        if args.host == 'local':
            prefix = ""
            ssh = False
        else:
            prefix = "ssh pi@"+args.host+".local "
            ssh = True

        if args.subparser == 'status':
            call_func(prefix + "sudo systemctl status "+args.unit, ssh)
        elif args.subparser == 'log':
            call_func(prefix + "sudo journalctl -f -u "+args.unit, ssh)
        elif args.subparser == 'start':
            call_func(prefix + "sudo systemctl start "+args.unit, ssh)
        elif args.subparser == 'stop':
            call_func(prefix + "sudo systemctl stop "+args.unit, ssh)
        elif args.subparser == 'restart':
            call_func(prefix + "sudo systemctl restart "+args.unit, ssh)
        elif args.subparser == 'enable':
            call_func(prefix + "sudo systemctl enable "+args.unit, ssh)
        elif args.subparser == 'disable':
            call_func(prefix + "sudo systemctl disable "+args.unit, ssh)
    else:
        parser.print_help()

