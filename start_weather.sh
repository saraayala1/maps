#!/bin/bash
# start_weather.sh
# Boot wrapper for weather_lights.py
# Sources /home/javi/.env to inject WEATHERBIT_API_KEY, then launches the display script.
# Cron entry: @reboot /home/javi/start_weather.sh >> /home/javi/weather_lights.log 2>&1

source /home/javi/.env
python3 /home/javi/weather_lights.py 2>&1 | tee -a /home/javi/weather_lights.log &
