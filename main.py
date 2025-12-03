"""
Meshcore Telemetry Reader for Heltec V3 via USB Serial with BME280 Sensor
"""

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from meshcore import MeshCore, SerialConnection, ConnectionManager, EventType

# Create logs directory
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Create timestamped log file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = logs_dir / f"meshcore_{timestamp}.log"

# Configure logging with both file and console output
logging.basicConfig(
    level=logging.DEBUG,  # More verbose
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Logging to: {log_file}")

# BME280 sensor setup
bme280_sensor = None
try:
    import board
    import busio
    import adafruit_bme280.advanced as adafruit_bme280
    
    logger.info("Initializing BME280 sensor...")
    logger.info(f"Board detected: {board.board_id if hasattr(board, 'board_id') else 'Unknown'}")
    
    # Create I2C interface
    try:
        # First try the default I2C
        i2c = board.I2C()
        logger.debug("I2C interface created using board.I2C()")
    except Exception as e:
        # Fallback: create I2C explicitly
        logger.debug(f"board.I2C() failed: {e}, trying explicit busio.I2C()")
        i2c = busio.I2C(board.SCL, board.SDA)
        logger.debug(f"I2C interface created on SCL={board.SCL}, SDA={board.SDA}")
    
    # Scan for I2C devices
    logger.debug("Scanning I2C bus for devices...")
    while not i2c.try_lock():
        pass
    try:
        devices = i2c.scan()
        if devices:
            logger.info(f"Found {len(devices)} I2C device(s): {[hex(d) for d in devices]}")
        else:
            logger.warning("No I2C devices detected on the bus!")
            logger.warning("Check BME280 wiring:")
            logger.warning("  VCC → 3.3V, GND → Ground, SDA → GPIO2 (Pin 3), SCL → GPIO3 (Pin 5)")
    finally:
        i2c.unlock()
    
    # Try both common I2C addresses (0x76 and 0x77)
    for address in [0x76, 0x77]:
        try:
            logger.debug(f"Attempting to initialize BME280 at address 0x{address:02x}")
            bme280_sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=address)
            bme280_sensor.sea_level_pressure = 1013.25  # Standard sea level pressure
            logger.info(f"✓ BME280 sensor initialized successfully at address 0x{address:02x}")
            
            # Test read
            test_temp = bme280_sensor.temperature
            logger.info(f"  Temperature reading: {test_temp:.2f}°C")
            break
        except ValueError as e:
            logger.debug(f"BME280 not at 0x{address:02x}: {e}")
            continue
        except Exception as e:
            logger.debug(f"Error at 0x{address:02x}: {type(e).__name__}: {e}")
            continue
    
    if bme280_sensor is None:
        raise Exception("BME280 not found at addresses 0x76 or 0x77. Check wiring and run: python check_i2c_wiring.py")
        
except ImportError as e:
    logger.error(f"BME280 libraries not installed: {e}")
    logger.error("Run: pip install adafruit-circuitpython-bme280 adafruit-blinka")
except Exception as e:
    logger.warning(f"BME280 sensor not available: {e}")
    logger.warning("Continuing without BME280 sensor...")
    logger.warning("Run 'python check_i2c_wiring.py' for detailed diagnostics")


def read_bme280():
    """Read BME280 sensor data."""
    if bme280_sensor is None:
        return None
    
    try:
        data = {
            'temperature_c': round(bme280_sensor.temperature, 2),
            'temperature_f': round(bme280_sensor.temperature * 9/5 + 32, 2),
            'humidity': round(bme280_sensor.relative_humidity, 2),
            'pressure_hpa': round(bme280_sensor.pressure, 2),
            'altitude_m': round(bme280_sensor.altitude, 2),
        }
        return data
    except Exception as e:
        logger.error(f"Error reading BME280: {e}")
        return None


async def handle_event(event):
    """Handle events from the Meshcore device."""
    event_type = event.type
    event_payload = event.payload
    event_attrs = event.attributes
    
    # Log all events to file with full details
    logger.info(f"Event received: {event_type.name}")
    logger.info(f"  Payload: {event_payload}")
    logger.info(f"  Attributes: {event_attrs}")
    
    # Display all events to console with verbose formatting
    print(f"\n{'='*70}")
    print(f"🔔 EVENT: {event_type.name}")
    print(f"{'='*70}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Display payload with proper formatting
    if event_payload:
        print(f"\n📦 PAYLOAD:")
        if isinstance(event_payload, dict):
            for key, value in event_payload.items():
                print(f"   • {key}: {value}")
        else:
            print(f"   {event_payload}")
    
    # Display attributes if present
    if event_attrs:
        print(f"\n🏷️  ATTRIBUTES:")
        for key, value in event_attrs.items():
            print(f"   • {key}: {value}")
    
    # Add specific handling for different event types
    if event_type == EventType.BATTERY:
        print(f"\n🔋 Battery Status:")
        if 'level' in event_payload:
            print(f"   Level: {event_payload['level']}%")
        if 'voltage' in event_payload:
            print(f"   Voltage: {event_payload['voltage']}V")
    
    elif event_type == EventType.DEVICE_INFO:
        print(f"\n📱 Device Information:")
        for key in ['device_id', 'node_id', 'hardware', 'firmware']:
            if key in event_payload:
                print(f"   {key.replace('_', ' ').title()}: {event_payload[key]}")
    
    elif event_type == EventType.TELEMETRY_RESPONSE:
        print(f"\n📊 Telemetry Data:")
        for key, value in event_payload.items():
            print(f"   {key}: {value}")
    
    elif event_type in [EventType.CONTACT_MSG_RECV, EventType.CHANNEL_MSG_RECV]:
        print(f"\n💬 Message Received:")
        if 'from' in event_payload:
            print(f"   From: {event_payload['from']}")
        if 'to' in event_payload:
            print(f"   To: {event_payload['to']}")
        if 'text' in event_payload:
            print(f"   Text: {event_payload['text']}")
        if 'message' in event_payload:
            print(f"   Message: {event_payload['message']}")
    
    elif event_type == EventType.NEW_CONTACT:
        print(f"\n👤 New Contact Discovered:")
        if 'node_id' in event_payload:
            print(f"   Node ID: {event_payload['node_id']}")
    
    print(f"{'='*70}\n")


async def main():
    """Main function to connect to Meshcore device and read telemetry."""
    # USB serial port (adjust if your device is on a different port)
    serial_port = "/dev/ttyUSB0"
    baudrate = 115200
    connection_timeout = 30  # seconds - increased for slower devices
    
    logger.info("="*60)
    logger.info("Meshcore Telemetry Reader Starting")
    logger.info("="*60)
    logger.info(f"Serial Port: {serial_port}")
    logger.info(f"Baud Rate: {baudrate}")
    logger.info(f"Connection Timeout: {connection_timeout}s")
    
    print(f"\nConnecting to Meshcore device on {serial_port} at {baudrate} baud...")
    print(f"Logging to: {log_file}\n")
    
    meshcore = None
    connection_manager = None
    
    try:
        # Create serial connection
        logger.debug(f"Creating SerialConnection({serial_port}, {baudrate})")
        connection = SerialConnection(serial_port, baudrate)
        logger.debug("SerialConnection created successfully")
        
        logger.debug("Creating ConnectionManager")
        connection_manager = ConnectionManager(connection)
        logger.debug("ConnectionManager created successfully")
        
        # Initialize Meshcore client with debug logging and timeout
        logger.debug("Initializing MeshCore client")
        meshcore = MeshCore(
            connection_manager,
            debug=True,  # Enable debug mode
            auto_reconnect=True,  # Enable auto reconnect
            default_timeout=connection_timeout
        )
        logger.info("MeshCore client initialized")
        
        # Subscribe to all relevant events using meshcore.subscribe directly
        events_to_monitor = [
            EventType.BATTERY,
            EventType.DEVICE_INFO,
            EventType.TELEMETRY_RESPONSE,
            EventType.CONTACT_MSG_RECV,
            EventType.CHANNEL_MSG_RECV,
            EventType.CONNECTED,
            EventType.DISCONNECTED,
            EventType.NEW_CONTACT,
            EventType.ADVERTISEMENT,
            EventType.TRACE_DATA,
            EventType.SELF_INFO,
            EventType.STATUS_RESPONSE,
        ]
        
        logger.info(f"Subscribing to {len(events_to_monitor)} event types...")
        for event in events_to_monitor:
            logger.debug(f"  Subscribing to: {event.name}")
            meshcore.subscribe(event, handle_event)
        logger.info("Event subscriptions completed")
        
        print("Subscribed to events. Connecting to device...\n")
        
        # Connect to device - don't use strict timeout as SELF_INFO may be delayed
        logger.info("Initiating connection to device...")
        try:
            # Connect without strict timeout - let it establish connection
            await meshcore.connect()
            logger.info("✓ Connection initiated to Meshcore device!")
            print("✓ Connection initiated!\n")
        except Exception as e:
            logger.error(f"Connection failed: {e}", exc_info=True)
            print(f"\n✗ Connection failed: {e}")
            return
        
        # Start auto message fetching to retrieve queued messages
        logger.info("Starting auto message fetching...")
        try:
            await meshcore.start_auto_message_fetching()
            logger.info("Auto message fetching started")
        except Exception as e:
            logger.warning(f"Could not start auto message fetching: {e}")
        
        # Access device commands through commands module
        logger.debug("Setting up device commands")
        from meshcore.commands import DeviceCommands
        device_commands = DeviceCommands()
        device_commands.set_connection(connection)
        device_commands.set_dispatcher(meshcore)
        device_commands.set_reader(meshcore)
        logger.debug("Device commands configured")
        
        # Give device a moment to stabilize
        logger.debug("Waiting 1 second for device to stabilize...")
        await asyncio.sleep(1)
        
        # Request device information
        logger.info("Sending device query request...")
        try:
            result = await asyncio.wait_for(
                device_commands.send_device_query(),
                timeout=10
            )
            logger.info(f"Device query result: {result}")
        except asyncio.TimeoutError:
            logger.warning("Device query request timed out - device may respond later")
        except Exception as e:
            logger.warning(f"Device query failed: {e}")
        
        # Wait a bit before next command
        await asyncio.sleep(1)
        
        # Request battery status
        logger.info("Requesting battery status...")
        try:
            result = await asyncio.wait_for(
                device_commands.get_bat(),
                timeout=10
            )
            logger.info(f"Battery status result: {result}")
        except asyncio.TimeoutError:
            logger.warning("Battery request timed out - device may respond later")
        except Exception as e:
            logger.warning(f"Battery request failed: {e}")
        
        # Keep the connection alive and listen for events
        logger.info("Entering main event loop")
        print("\n" + "="*60)
        print("Reading telemetry data (Ctrl+C to stop)")
        print("="*60 + "\n")
        
        try:
            last_sensor_read = 0
            last_status_log = 0
            sensor_interval = 10  # Read BME280 every 10 seconds
            status_interval = 30  # Log status every 30 seconds
            loop_count = 0
            
            while True:
                loop_count += 1
                current_time = time.time()
                
                # Log periodic status
                if (current_time - last_status_log) >= status_interval:
                    connected_status = getattr(meshcore, 'is_connected', None)
                    if callable(connected_status):
                        is_conn = connected_status()
                    else:
                        is_conn = connected_status if connected_status is not None else "unknown"
                    logger.debug(f"Status: Running (loops: {loop_count}, connected: {is_conn})")
                    last_status_log = current_time
                
                # Read BME280 sensor periodically
                if bme280_sensor and (current_time - last_sensor_read) >= sensor_interval:
                    logger.debug("Reading BME280 sensor...")
                    sensor_data = read_bme280()
                    if sensor_data:
                        print(f"\n{'='*70}")
                        print(f"🌡️  BME280 ENVIRONMENTAL SENSOR READING")
                        print(f"{'='*70}")
                        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"\n📊 Measurements:")
                        print(f"   🌡️  Temperature: {sensor_data['temperature_c']}°C ({sensor_data['temperature_f']}°F)")
                        print(f"   💧 Humidity: {sensor_data['humidity']}%")
                        print(f"   🔽 Pressure: {sensor_data['pressure_hpa']} hPa")
                        print(f"   ⛰️  Altitude: {sensor_data['altitude_m']} m")
                        print(f"{'='*70}\n")
                        logger.info(f"BME280 Reading: Temp={sensor_data['temperature_c']}°C, Humidity={sensor_data['humidity']}%, Pressure={sensor_data['pressure_hpa']}hPa")
                    last_sensor_read = current_time
                
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user (Ctrl+C)")
            print("\n\nShutting down...")
        
        # Disconnect gracefully
        if meshcore:
            logger.info("Disconnecting from device...")
            try:
                # Stop auto message fetching first
                try:
                    await asyncio.wait_for(meshcore.stop_auto_message_fetching(), timeout=3)
                    logger.debug("Auto message fetching stopped")
                except Exception as e:
                    logger.debug(f"Could not stop auto fetch: {e}")
                
                # Then disconnect
                await asyncio.wait_for(meshcore.disconnect(), timeout=5)
                logger.info("✓ Disconnected successfully")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
        
    except FileNotFoundError as e:
        logger.error(f"Serial port {serial_port} not found", exc_info=True)
        print(f"\n✗ Error: Serial port {serial_port} not found.")
        print("\nAvailable serial ports:")
        try:
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            if ports:
                for port in ports:
                    print(f"  - {port.device}: {port.description}")
                    logger.info(f"Available port: {port.device} - {port.description}")
            else:
                print("  (No serial ports found)")
                logger.warning("No serial ports found on system")
        except Exception as e:
            logger.error(f"Could not list ports: {e}", exc_info=True)
    
    except KeyboardInterrupt:
        logger.info("Interrupted during startup")
        print("\n\nInterrupted during startup")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
        print(f"\nCheck the log file for details: {log_file}")
    
    finally:
        logger.info("="*60)
        logger.info("Meshcore Telemetry Reader Stopped")
        logger.info("="*60)


if __name__ == "__main__":
    asyncio.run(main())
