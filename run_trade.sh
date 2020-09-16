#!/bin/bash

if pgrep -af run_trade.py
	then
	  nohup python3 run_trade.py & ls
		echo "+"
	else
		echo "-"
fi
