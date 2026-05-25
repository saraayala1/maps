#!/usr/bin/env bash
# stop_weather.sh — stop the weather lights script and clear the LED strip.
# The SIGTERM handler in weather_lights.py fills all LEDs black before exiting.
# Usage: ~/stop_weather.sh
# Called by cron off-entries. Append output to ~/weather_lights.log.

pkill -f weather_lights.py
