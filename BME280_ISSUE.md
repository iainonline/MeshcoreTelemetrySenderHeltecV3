# BME280 Sensor Issue Summary

## Current Status
❌ **BME280 sensor is NOT detected on the I2C bus**

## What We Know

### System Configuration
- **Device**: Raspberry Pi 5 Model B Rev 1.0
- **I2C Enabled**: Yes (`dtparam=i2c_arm=on`)
- **User Permissions**: ✓ Member of `i2c` group
- **I2C Devices Available**: `/dev/i2c-1`, `/dev/i2c-13`, `/dev/i2c-14`
- **Software**: All required Python packages installed correctly

### Test Results
1. ✓ I2C interface creates successfully
2. ✓ I2C bus scanning works
3. ❌ No devices found at address 0x76 or 0x77
4. ❌ `i2cdetect -y 1` shows empty bus

### What This Means
**This is a hardware wiring issue, not a software problem.**

The BME280 sensor is either:
1. Not physically connected
2. Incorrectly wired
3. Damaged/defective
4. Using wrong power voltage (5V instead of 3.3V)

## Expected vs Actual

### Expected Wiring (for Raspberry Pi)
```
BME280 → Raspberry Pi
VCC    → Pin 1 or 17 (3.3V)
GND    → Pin 6, 9, 14, etc (Ground)
SDA    → Pin 3 (GPIO2)
SCL    → Pin 5 (GPIO3)
```

### What `i2cdetect` Should Show
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
...
70: -- -- -- -- -- -- 76 --    (BME280 at 0x76)
```

### What We Actually See
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
...
70: -- -- -- -- -- -- -- --    (nothing)
```

## Troubleshooting Steps

### 1. Verify Physical Connections
Run the diagnostic:
```bash
python check_i2c_wiring.py
```

Check each wire:
- [ ] VCC connected to 3.3V (NOT 5V!)
- [ ] GND connected to Ground
- [ ] SDA connected to GPIO2 (Pin 3)
- [ ] SCL connected to GPIO3 (Pin 5)
- [ ] All connections are firm and secure

### 2. Check Power
- [ ] BME280 LED is lit (if module has LED)
- [ ] Measure voltage at VCC pin = 3.3V
- [ ] **IMPORTANT**: If you accidentally used 5V, the sensor may be damaged

### 3. Test with Multimeter
- [ ] Continuity test from Raspberry Pi GPIO2 to BME280 SDA
- [ ] Continuity test from Raspberry Pi GPIO3 to BME280 SCL
- [ ] Verify no shorts between VCC and GND

### 4. Compare with Meshtastic Setup
You mentioned this worked with Meshtastic. Check:
- [ ] Are you using the SAME physical pins?
- [ ] Did Meshtastic use I2C bus 1 (GPIO2/3)?
- [ ] Could Meshtastic have used a different I2C bus?
- [ ] Was the sensor moved or rewired since then?

### 5. Try Different I2C Bus (if applicable)
Some setups use alternate I2C buses:
```bash
# Check all buses
i2cdetect -y 1
i2cdetect -y 0  # Some systems
```

### 6. Reboot After Wiring Changes
```bash
sudo reboot
```

## Diagnostic Tools Included

### 1. `check_i2c_wiring.py`
Simple wiring verification tool
- Scans I2C bus
- Shows expected wiring
- Provides troubleshooting steps

### 2. `test_bme280.py`
Detailed sensor testing
- Checks Python packages
- Tests I2C interface creation
- Attempts sensor initialization
- Provides detailed error messages

### 3. Manual Testing
```bash
# Check I2C is enabled
ls -l /dev/i2c*

# Scan bus 1
i2cdetect -y 1

# Check system logs
dmesg | grep i2c

# Verify permissions
groups  # should include 'i2c'
```

## Next Steps

1. **Physical Inspection**: Carefully check every wire connection
2. **Power Verification**: Confirm 3.3V at BME280 VCC pin
3. **Test Sensor**: Try sensor with a simple test program
4. **Consider Replacement**: If sensor worked before but not now, it may be damaged

## If Sensor Is Damaged

If you determine the sensor is damaged:
1. BME280 modules are inexpensive (~$5-10)
2. Order from: Adafruit, SparkFun, or Amazon
3. Ensure new module supports 3.3V I2C
4. Some modules need pull-up resistors (most have them built-in)

## Software Works Correctly

The good news: **Your Meshcore telemetry reader software is working perfectly!**

- ✓ Connects to Heltec V3 device
- ✓ Receives CONNECTED event
- ✓ Auto message fetching works
- ✓ BME280 code correctly handles missing sensor
- ✓ Continues operation without sensor

The BME280 feature will work immediately once the hardware wiring is corrected.

## Questions to Answer

1. Is the BME280 physically connected right now?
2. Which pins are you using on the Raspberry Pi?
3. Can you see any LED on the BME280 module?
4. What voltage are you supplying (3.3V or 5V)?
5. Did this sensor work recently, or is this a new setup?

Run `python check_i2c_wiring.py` and share the output!
