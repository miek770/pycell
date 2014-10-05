#!/usr/bin/python
#-*- coding: utf-8 -*-

import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

import Image
import ImageDraw
import ImageFont

from multiprocessing import Process, Pipe
import keys

from lxml import etree

class oled:
    def __init__(self, menufile='menu.xml'):

        RST = 'P9_13'
        DC = 'P9_14'
        SPI_PORT = 1
        SPI_DEVICE = 0

        # 128x64 display with hardware SPI:
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

        # Initialize library.
        self.disp.begin()

        # Clear display.
        self.disp.clear()
        self.disp.display()

        self.buff = list()
        self.cursor = 0
        self.maxlines = 6

        # Initialize keypad
        self.keypad_parent_conn, self.keypad_child_conn = Pipe()
        self.keypad_sub = Process(target=keys.loop, args=(self.keypad_child_conn, ))
        self.keypad_sub.start()

        self.menu = etree.parse(menufile)

    def refresh(self):
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        width = self.disp.width
        height = self.disp.height

        image = Image.new('1', (width, height))
        draw = ImageDraw.Draw(image)
        #font = ImageFont.load_default()
        font = ImageFont.truetype('Minecraftia-Regular.ttf', 8)

        i = 0
        for l in range(self.cursor, len(self.buff)):
            if i < self.maxlines:
                draw.text((0, 10*i), self.buff[l], font=font, fill=255)
                i += 1

        # Display image.
        self.disp.image(image)
        self.disp.display()

    def scroll_down(self):
        if self.cursor < len(self.buff) - 1:
            self.cursor += 1
            self.refresh()

    def scroll_up(self):
        if self.cursor > 0:
            self.cursor -= 1
            self.refresh()

    def welcome(self):
        self.buff.append(u'1 Hello world!')
        self.buff.append(u'2 Mon nom est Michel.')
        self.buff.append(u'3 Ceci est un test.')
        self.buff.append(u'4 Je veux voir si ca')
        self.buff.append(u'5 marche, mais je ne')
        self.buff.append(u'6 suis pas inquieté')
        self.cursor = len(self.buff) - 6
        self.refresh()

    def loop(self):
        self.welcome()
        
        while True:
            if self.keypad_parent_conn.poll():
                key = self.keypad_parent_conn.recv()
                if key == '2':
                    self.scroll_up()
                elif key == '8':
                    self.scroll_down()
            time.sleep(0.1)

if __name__ == '__main__':
    oled().loop()

