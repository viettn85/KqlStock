#!/bin/bash
cd /Users/viet_tran/Workplace/viettn85/KQL/KqlStock/
nohup python3 src/bots/scanner.py > logs/kqls.log &
# https://stackoverflow.com/questions/29338066/run-python-script-at-os-x-startup
