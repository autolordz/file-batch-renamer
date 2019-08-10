#!/bin/bash
nohup java -Djava.awt.headless=true -jar /tmp/tika-server.jar --host=yourhost --port=3232 >/dev/null &
nohup python3 /tmp/flask_app/app.py >/dev/null &
