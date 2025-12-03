#!/usr/bin/env python3
"""
BME280 Sensor Diagnostic Script
Tests I2C connectivity and BME280 sensor detection
"""

import sys
import os

print("=" * 70)
print("BME280 Sensor Diagnostic Tool")
print("=" * 70)

# Test 1: Check I2C device files
print("\n1. Checking I2C device files...")
i2c_devices = []
for i in range(20):
    dev_path = f"/dev/i2c-{i}"
    if os.path.exists(dev_path):
        i2c_devices.append(i)
        print(f"   ✓ Found: {dev_path}")

if not i2c_devices:
    print("   ✗ No I2C devices found!")
    print("   → Run: sudo raspi-config → Interface Options → I2C → Enable")
    sys.exit(1)

# Test 2: Check Python packages
print("\n2. Checking Python packages...")
try:
    import board
    print("   ✓ board module imported")
except ImportError as e:
    print(f"   ✗ Failed to import board: {e}")
    print("   → Run: pip install adafruit-blinka")

try:
    import adafruit_bme280
    print("   ✓ adafruit_bme280 module imported")
except ImportError as e:
    print(f"   ✗ Failed to import adafruit_bme280: {e}")
    print("   → Run: pip install adafruit-circuitpython-bme280")

try:
    import busio
    print("   ✓ busio module imported")
except ImportError as e:
    print(f"   ✗ Failed to import busio: {e}")

# Test 3: Check board I2C pins
print("\n3. Checking board I2C configuration...")
try:
    import board
    print(f"   Board ID: {board.board_id if hasattr(board, 'board_id') else 'Unknown'}")
    if hasattr(board, 'SCL'):
        print(f"   SCL Pin: {board.SCL}")
    if hasattr(board, 'SDA'):
        print(f"   SDA Pin: {board.SDA}")
    
    # Try to create I2C interface
    print("\n4. Creating I2C interface...")
    try:
        i2c = board.I2C()
        print("   ✓ I2C interface created")
        
        # Scan for I2C devices
        print("\n5. Scanning I2C bus for devices...")
        while not i2c.try_lock():
            pass
        
        try:
            devices = i2c.scan()
            if devices:
                print(f"   ✓ Found {len(devices)} device(s):")
                for device in devices:
                    print(f"      - 0x{device:02x}")
                    if device == 0x76:
                        print("        → This is likely BME280 at primary address")
                    elif device == 0x77:
                        print("        → This is likely BME280 at alternate address")
            else:
                print("   ✗ No I2C devices found on the bus!")
                print("   → Check wiring:")
                print("      - VCC/VIN to 3.3V")
                print("      - GND to Ground")
                print("      - SDA to GPIO2 (Pin 3)")
                print("      - SCL to GPIO3 (Pin 5)")
        finally:
            i2c.unlock()
            
    except Exception as e:
        print(f"   ✗ Failed to create I2C interface: {e}")
        print(f"   Error type: {type(e).__name__}")
        
except ImportError as e:
    print(f"   ✗ Cannot import board module: {e}")
    sys.exit(1)

# Test 6: Try to initialize BME280
print("\n6. Testing BME280 initialization...")
try:
    import board
    import adafruit_bme280
    
    i2c = board.I2C()
    
    for address in [0x76, 0x77]:
        try:
            print(f"   Trying address 0x{address:02x}...")
            bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=address)
            print(f"   ✓ BME280 initialized at 0x{address:02x}!")
            
            # Try reading
            print("\n7. Reading sensor data...")
            try:
                temp = bme280.temperature
                humidity = bme280.relative_humidity
                pressure = bme280.pressure
                
                print(f"   ✓ Temperature: {temp:.2f}°C")
                print(f"   ✓ Humidity: {humidity:.2f}%")
                print(f"   ✓ Pressure: {pressure:.2f} hPa")
                print("\n✓ BME280 sensor is working correctly!")
                sys.exit(0)
            except Exception as e:
                print(f"   ✗ Failed to read sensor: {e}")
        except Exception as e:
            print(f"   ✗ Failed at 0x{address:02x}: {e}")
            continue
    
    print("\n   ✗ BME280 not found at either 0x76 or 0x77")
    
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Diagnostic complete")
print("=" * 70)
