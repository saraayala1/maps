# Pi Weather Lights — Setup Guide

## One-time Pi Configuration

Do these steps once via SSH before running the script.

### 1. Enable SPI

```bash
ssh javi@map.local
sudo nano /boot/firmware/config.txt
```

Add or uncomment:
```
dtparam=spi=on
```

Save, then reboot:
```bash
sudo reboot
```

> Note: On older Pi OS versions the file is `/boot/config.txt` instead.

### 2. Add User to SPI and GPIO Groups

```bash
sudo usermod -a -G spi,gpio javi
```

Log out and back in (or reboot) for group changes to take effect.

### 3. Install Python Dependencies

```bash
pip3 install adafruit-circuitpython-dotstar requests
```

### 4. Configure Location Coordinates

Open `weather_lights.py` and set your coordinates near the top:

```python
LAT = 25.7617    # replace with your latitude
LON = -80.1918   # replace with your longitude
```

Find your coordinates at https://www.latlong.net/

### 5. Set Weatherbit API Key

Get a free API key at https://www.weatherbit.io/account/create

Create `~/.env` on the Pi with your key:
```bash
echo 'WEATHERBIT_API_KEY=your_key_here' > ~/.env
chmod 600 ~/.env
```

> The boot wrapper (`start_weather.sh`) sources this file automatically. Do not use quotes around the value.

### 6. Copy Scripts to the Pi

```bash
scp weather_lights.py javi@map.local:/home/javi/weather_lights.py
scp start_weather.sh javi@map.local:/home/javi/start_weather.sh
chmod +x /home/javi/start_weather.sh
```

### 7. Verify Hardware

Run the hardware test:
```bash
ssh javi@map.local "python3 weather_lights.py --test-hardware"
```

The strip should fill green for 2 seconds, then go dark. If you get a
`PermissionError`, re-check step 2 (groups) and reboot.

### 8. Wire Up Auto-Start (cron @reboot)

Add the boot entry to javi's crontab:
```bash
ssh javi@map.local "crontab -e"
```

Add this line at the bottom:
```
@reboot /home/javi/start_weather.sh >> /home/javi/weather_lights.log 2>&1
```

Save and exit. Verify it saved:
```bash
ssh javi@map.local "crontab -l"
```

## Running Manually

```bash
ssh javi@map.local "/home/javi/start_weather.sh"
```

Or directly without the wrapper (requires `WEATHERBIT_API_KEY` already exported):
```bash
ssh javi@map.local "python3 weather_lights.py"
```

Runs indefinitely, refreshing weather every hour. Press Ctrl+C to stop.

## Checking the Log

After a boot or manual start, tail the log to confirm it's running:
```bash
ssh javi@map.local "tail -20 ~/weather_lights.log"
```

The log shows the fetched temperature and active conditions on each hourly refresh.
