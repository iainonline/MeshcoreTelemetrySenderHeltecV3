#!/usr/bin/env python3
"""
Simple I2C Bus Scanner - Check if BME280 is wired correctly
"""

import board
import busio
import time

print("=" * 70)
print("I2C Bus Scanner for BME280")
print("=" * 70)

print("\nExpected wiring for BME280 on Raspberry Pi:")
print("  BME280 VCC/VIN → Raspberry Pi 3.3V  (Pin 1 or 17)")
print("  BME280 GND     → Raspberry Pi Ground (Pin 6, 9, 14, 20, 25, 30, 34, or 39)")
print("  BME280 SDA     → Raspberry Pi GPIO2  (Pin 3)")
print("  BME280 SCL     → Raspberry Pi GPIO3  (Pin 5)")
print("\n" + "=" * 70)

# Create I2C bus
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    print("\n✓ I2C bus created successfully")
    print(f"  SCL: GPIO{board.SCL}")
    print(f"  SDA: GPIO{board.SDA}")
except Exception as e:
    print(f"\n✗ Failed to create I2C bus: {e}")
    exit(1)

# Scan for devices
print("\nScanning I2C bus...")
print("This may take a few seconds...\n")

for attempt in range(3):
    if attempt > 0:
        print(f"\nRetry {attempt}...")
        time.sleep(1)
    
    while not i2c.try_lock():
        pass
    
    try:
        devices = i2c.scan()
        
        if devices:
            print(f"✓ Found {len(devices)} I2C device(s):")
            for device_address in devices:
                print(f"\n  Address: 0x{device_address:02X} (decimal {device_address})")
                
                if device_address == 0x76:
                    print("    → BME280 detected at primary address (0x76)")
                    print("    → Your sensor is connected correctly!")
                elif device_address == 0x77:
                    print("    → BME280 detected at alternate address (0x77)")
                    print("    → Your sensor is connected correctly!")
                    print("    → Some BME280 modules use 0x77 by default")
                elif device_address == 0x3C or device_address == 0x3D:
                    print("    → This is likely an OLED display")
                else:
                    print(f"    → Unknown I2C device")
            
            if 0x76 in devices or 0x77 in devices:
                print("\n" + "=" * 70)
                print("SUCCESS! BME280 is properly connected.")
                print("=" * 70)
                i2c.unlock()
                exit(0)
        else:
            print("✗ No I2C devices found")
            
    finally:
        i2c.unlock()

print("\n" + "=" * 70)
print("PROBLEM: BME280 not detected on I2C bus")
print("=" * 70)
print("\nTroubleshooting steps:")
print("1. Check physical connections:")
print("   - Ensure all wires are firmly connected")
print("   - Check for loose connections or damaged wires")
print("   - Verify you're using the correct GPIO pins (2 and 3)")
print("\n2. Check power:")
print("   - BME280 needs 3.3V (NOT 5V - may damage sensor)")
print("   - Verify power LED on BME280 module is lit (if present)")
print("\n3. Try with i2cdetect command:")
print("   Run: i2cdetect -y 1")
print("   Should show device at 76 or 77")
print("\n4. Check if I2C is enabled:")
print("   Run: sudo raspi-config")
print("   → Interface Options → I2C → Enable")
print("\n5. If you just connected the sensor:")
print("   - Power cycle: sudo reboot")
print("\n6. Test with a multimeter:")
print("   - Check continuity of SDA and SCL connections")
print("   - Verify 3.3V at sensor VCC pin")
print("=" * 70)
