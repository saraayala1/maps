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

Set the environment variable before running:
```bash
export WEATHERBIT_API_KEY="your_key_here"
```

For persistence, add to `~/.bashrc`:
```bash
echo 'export WEATHERBIT_API_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### 6. Verify Hardware

Copy `weather_lights.py` to the Pi and run the hardware test:
```bash
python3 weather_lights.py --test-hardware
```

The strip should fill green for 2 seconds, then go dark. If you get a
`PermissionError`, re-check step 2 (groups) and reboot.

## Running the Script

```bash
python3 weather_lights.py
```

Runs indefinitely, refreshing weather every hour. Press Ctrl+C to stop.
