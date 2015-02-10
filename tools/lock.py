#!/usr/bin/python
import bitsharesrpc
import config

if __name__ == "__main__":
 rpc = bitsharesrpc.client(config.url, config.user, config.passwd)
 print rpc.wallet_open("delegate")
 print rpc.lock()
