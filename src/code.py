import board
import neopixel
import time
import microcontroller
import struct
import json

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket
from adafruit_ble import BLERadio
from adafruit_ble.uuid import VendorUUID
from adafruit_ble.services import Service
from adafruit_ble.services.standard import GenericAccess
from adafruit_ble.advertising import Advertisement, String
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from brightness_packet import BrightnessPacket, SettingsRequestPacket

# initialize bluetooth radio
# ble = BLERadio()
# ble.name = "A Glass Jar"
# uart_service = UARTService()
# uart_service.uuid = VendorUUID("622b6b5e-b514-4be9-81d4-e13ba87ba54f")
# advertisement = ProvideServicesAdvertisement(uart_service)

# initialize pixels
board_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0).show()
pixels = neopixel.NeoPixel(
    board.D5, 7, brightness=0.05, auto_write=False, pixel_order=neopixel.RGBW
)

class Logger:
    def info(self, message):
        print("[INFO]: " + message)
    
    def error(self, message):
        print("[ERROR]: " + message)

logger = Logger()

class Device:
    ble = BLERadio()
    uart_service = UARTService()

    def __init__(self):
        save_config = False
        
        try:
            with open('/config', 'r') as reader:
                self.config = json.loads(reader.read())
        except Exception as err:
            print('${0}'.format(err))
            self.config = {
                "name": "A Glass Jar",
                "color": (123, 20, 4),
                "brightness": 20
            }
            save_config = True

        print(self.config)
        self.ble.name = self.config['name']
        self.set_color((0, 0, 0))
        self.set_color(self.config['color'], (0, 0, 0), save_config)
        self.set_brightness(self.config['brightness'], save_config)
    
    @property
    def connected(self):
        return self.ble.connected
    
    def advertise(self):
        self.ble.start_advertising(ProvideServicesAdvertisement(self.uart_service))
    
    def send_config(self):
        self.uart_service.write(json.dumps(self.config))
        logger.info('wrote the config to rx')
    
    def set_color(self, to_color, from_color = None, save = True):
        step = 0.005

        if from_color == None:
            pixels.fill(to_color)
            pixels.show()
            return
        
        logger.info("transitioning color from " + str(from_color) + " to " + str(to_color))
        
        g_dir = -1 if to_color[0] < from_color[0] else 1
        r_dir = -1 if to_color[1] < from_color[1] else 1
        b_dir = -1 if to_color[2] < from_color[2] else 1
        temp_color = list(from_color)

        while temp_color[0] != to_color[0] or temp_color[1] != to_color[1] or temp_color[2] != to_color[2]:
            if temp_color[0] != to_color[0]:
                temp_color[0] = temp_color[0] + g_dir
            if temp_color[1] != to_color[1]:
                temp_color[1] = temp_color[1] + r_dir
            if temp_color[2] != to_color[2]:
                temp_color[2] = temp_color[2] + b_dir
            
            pixels.fill(temp_color)
            pixels.show()
            time.sleep(step)

        logger.info("done transitioning color")

        if save:
            self.__save_config('color', tuple(temp_color))
    
    def set_brightness(self, val, save = True):
        current_brightness = self.config['brightness']
        logger.info("transitioning brightness from " + str(current_brightness) + " to " + str(val))
        time_step = 0.005
        value_step = 1 if current_brightness < val else -1
        temp_brightness = current_brightness

        while temp_brightness != val:
            temp_brightness += value_step
            pixels.brightness = temp_brightness / 100
            pixels.show()
            time.sleep(time_step)
    
        logger.info("done transitioning brightness")

        if save:
            self.__save_config('brightness', temp_brightness)            
    
    def accept_requests(self):
        while self.connected:
            # resets the board
            # microcontroller.reset()
            if self.uart_service.in_waiting:
                packet = Packet.from_stream(self.uart_service)
                if isinstance(packet, ColorPacket):
                    self.set_color(packet.color, self.config['color'])
                elif isinstance(packet, BrightnessPacket):
                    self.set_brightness(packet.brightness)
                elif isinstance(packet, SettingsRequestPacket):
                    self.send_config()

    def __save_config(self, key, val):
        self.config[key] = val
        try:
            with open('/config', 'w') as writer:
                writer.write(json.dumps(self.config))
        except OSError as err :
            logger.error("OS error: {0}".format(err))

def main():
    device = Device()
    while True:
        try:
            if not device.connected:
                device.advertise()
                while not device.connected:
                    pass

            while device.connected:
                device.accept_requests()
        except Exception as err:
            logger.error("Unexpected Error: {0}".format(err))

main()
