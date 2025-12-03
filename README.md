# Meshcore Telemetry Reader

Python application to read telemetry data from a Meshcore device (Heltec V3) via USB serial connection, with BME280 environmental sensor support.

## Features

- Connect to Meshcore device via USB serial (`/dev/ttyUSB0`)
- Monitor Meshcore events (messages, device info, battery, telemetry responses)
- Read BME280 sensor data (temperature, humidity, pressure, altitude)
- Real-time display of all telemetry data

## Hardware Requirements

- Heltec V3 device running Meshcore firmware
- USB connection to the device
- BME280 sensor (optional, connected via I2C)

## Setup

1. Create and activate the virtual environment:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Check your USB device:
   ```bash
   ls -l /dev/ttyUSB0
   ```

## Running the Project

```bash
python main.py
```

The program will:
- Connect to the Meshcore device on `/dev/ttyUSB0`
- Request device information and battery status
- Monitor all Meshcore events
- Read BME280 sensor data every 10 seconds (if available)
- Display all data in real-time

Press `Ctrl+C` to stop.

## Configuration

Edit `main.py` to change:
- `serial_port`: USB serial port (default: `/dev/ttyUSB0`)
- `baudrate`: Serial baud rate (default: `115200`)
- `sensor_interval`: BME280 reading interval in seconds (default: `10`)

## Project Structure

- `main.py` - Main entry point with Meshcore and BME280 integration
- `requirements.txt` - Project dependencies
- `venv/` - Virtual environment (not committed to git)

## Dependencies

- `meshcore` - Meshcore device communication library
- `pyserial` - Serial port communication
- `adafruit-circuitpython-bme280` - BME280 sensor library
- `adafruit-blinka` - CircuitPython compatibility layer
