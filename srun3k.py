import argparse
import socket
import time
import requests
import json
import sys

def encrypt(passwd, time):
    time = str(int(int(time) / 60))[::-1]
    return confusion(passwd, time)


def confusion(passwd, key):
    if len(passwd) > 16:
        passwd = passwd[:16]
    result = ""
    for i in range(len(passwd)):
        _pass = ord(passwd[i])
        _key = ord(key[i % len(key)])
        _pass = _pass ^ _key
        result += diffusion(_pass, i % 2)
    return result


def diffusion(num, isReversed):
    low = num & 0x0f
    high = num >> 4
    if not isReversed:
        return chr(low + 0x36) + chr(high + 0x63)
    else:
        return chr(high + 0x63) + chr(low + 0x36)


def keep_alive(uid):
    data = (int(uid)).to_bytes(8, 'little')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(data, ('202.204.67.15', 3335))
        reply = s.recv(1024)
    return reply



def login(username, password, ipaddr):
    url = "http://{}:3333/cgi-bin/do_login".format(ipaddr)
    data = {
        "username": username,
        "password": password,
        "drop": "0",
        "type": "2",
    }
    res = requests.post(url=url, data=data)
    timestamp = res.text.split('@')[-1]
    data['password'] = encrypt(password, timestamp)
    res = requests.post(url=url, data=data)
    uuid = res.text.split(',')[0]
    return uuid


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', type=str, help='Your username')
    parser.add_argument('-p', type=str, help='Your password')
    parser.add_argument('-hi', type=int, default=2, 
    	help='Heartbeat packets interval, in minute, decimal support, default as 2')
    parser.add_argument('-ip', type=str, help="Server's ip address")
    parser.add_argument('--resume', action='store_true', help='Restore from config')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()

    # restore argument
    if args.resume:
        with open('config.json') as f:
            d = json.load(f)
        for k, v in d.items():
            args.__dict__[k]=v
    else:
        # save argument
        with open('config.json','w') as f:
            json.dump(vars(args), f)
    if args.u and args.p and args.ip:
        uuid = login(args.u, args.p, args.ip)
    else:
        print("Please input username, password and ip address!")
        sys.exit(1)
    while True:
        try:
            reply = keep_alive(uuid)
            print("Keep alive data:{}".format(reply))
            time.sleep(60*args.hi)
        except:
            print("Keep alive error")
