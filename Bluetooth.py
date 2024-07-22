import time
import ubluetooth
from machine import Pin

class BLEPeripheral:
    def __init__(self, name, led_pin):
        self.name = name
        self.led = Pin(led_pin, Pin.OUT)  # Initialize the LED pin as output
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self.irq_handler)
        self.register_services()
        self.advertise()

    def irq_handler(self, event, data):
        print("Event:", event)
        print("Data:", data)
        
        # Check if the event matches expected BLE events
        if event == 1:  # This is a placeholder value; replace with correct event code if known
            conn_handle = data[0]
            print("Central connected, handle:", conn_handle)
            self.led_on()  # Turn on LED when a device connects
        elif event == 2:  # This is a placeholder value; replace with correct event code if known
            conn_handle = data[0]
            print("Central disconnected, handle:", conn_handle)
            self.led_off()  # Turn off LED when no devices are connected
            self.advertise()  # Restart advertising after disconnection
        elif event == 3:  # This is a placeholder value; replace with correct event code if known
            conn_handle, attr_handle = data
            value = self.ble.gatts_read(attr_handle)
            print("Data written from handle {}: {}".format(conn_handle, value))
            self.on_write(value, conn_handle)
        else:
            print("Unhandled event:", event)
            print("Event data:", data)

    def on_write(self, value, conn_handle):
        # Handle the data written to the characteristic
        command = value.decode('utf-8').strip()
        if command == "LED ON":
            self.led_on()
        elif command == "LED OFF":
            self.led_off()
        else:
            print("Unknown command from handle {}: {}".format(conn_handle, command))

    def led_on(self):
        self.led.value(1)  # Turn on the LED

    def led_off(self):
        self.led.value(0)  # Turn off the LED

    def register_services(self):
        service_uuid = ubluetooth.UUID('12345678-1234-5678-1234-56789abcdef0')
        char_uuid = ubluetooth.UUID('87654321-4321-6789-4321-fedcba987654')
        char = (char_uuid, ubluetooth.FLAG_WRITE | ubluetooth.FLAG_READ)
        service = (service_uuid, (char,))
        
        try:
            self.services = self.ble.gatts_register_services((service,))
            print("Services registered:", self.services)
            
            if self.services and len(self.services) > 0:
                for idx, service_data in enumerate(self.services):
                    print(f"Service {idx} data:", service_data)
                    
                    if len(service_data) >= 2:
                        self.service_handle = service_data[0]
                        self.char_handle = service_data[1][0]  # Assuming only one characteristic
                        print("Service handle:", self.service_handle)
                        print("Characteristic handle:", self.char_handle)
                    else:
                        print("Service data does not contain enough elements:", service_data)
            else:
                raise RuntimeError("No services registered or empty response")
        except Exception as e:
            print("Error in service registration:", e)

    def advertise(self):
        name = self.name
        adv_data = bytearray(b'\x02\x01\x06')  # General discoverable mode
        adv_data.extend(bytearray((len(name) + 1, 0x09)))  # Length of the name + 1 (for the 0x09 type byte)
        adv_data.extend(name.encode('utf-8'))  # Complete local name
        # Add more flags to ensure compatibility with both iPhone and Android
        adv_data.extend(b'\x03\x03\x12\x18')  # Complete list of 16-bit Service Class UUIDs
        adv_data.extend(b'\x05\x02\x12\x18\x00\x00')  # Incomplete list of 16-bit Service Class UUIDs
        self.ble.gap_advertise(100000, adv_data)
        print("Advertising as", name)

# Create BLE peripheral with LED connected to GPIO pin 2
ble_peripheral = BLEPeripheral("ESP32BLE", led_pin=2)

# Keep the script running
while True:
    time.sleep(1)

