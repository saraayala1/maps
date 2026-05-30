#!/usr/bin/env bash
# restart_lights.sh — stop weather lights and restart immediately.

/home/javi/stop_weather.sh
sleep 1
/home/javi/start_weather.sh
