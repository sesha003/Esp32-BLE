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
        if event == 1:  # Assuming 1 corresponds to central connection
            print("Central connected")
            self.led_on()  # Turn on LED
        elif event == 2:  # Assuming 2 corresponds to central disconnection
            print("Central disconnected")
            self.led_off()  # Turn off LED
            self.advertise()  # Restart advertising after disconnection
        else:
            print("Unhandled event:", event)
            print("Event data:", data)

    def led_on(self):
        self.led.value(1)  # Turn on the LED

    def led_off(self):
        self.led.value(0)  # Turn off the LED

    def register_services(self):
        service_uuid = ubluetooth.UUID('12345678-1234-5678-1234-56789abcdef0')
        char_uuid = ubluetooth.UUID('87654321-4321-6789-4321-fedcba987654')
        char = (char_uuid, ubluetooth.FLAG_WRITE)
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
        self.ble.gap_advertise(100000, adv_data)
        print("Advertising as", name)

# Create BLE peripheral with LED connected to GPIO pin 2
ble_peripheral = BLEPeripheral("ESP32BLE", led_pin=2)

# Keep the script running
while True:
    time.sleep(1)

