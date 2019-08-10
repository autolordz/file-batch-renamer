#!/bin/bash
ps -ef | grep tika-server | grep -v grep | awk '{print $2}' | xargs kill -9
ps -ef | grep flask_app | grep -v grep | awk '{print $2}' | xargs kill -9

