#!/bin/bash

if pgrep -af trade/run_trade.py
	then
	  nohup python3 trade/run_trade.py & ls
	else
fi
