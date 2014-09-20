#!/root/cell/bin/python

import time
import Adafruit_BBIO.SPI as SPI
import Adafruit_SSD1306

import Image
import ImageDraw
import ImageFont

# A modifier pour le Arietta G25
RST = 'P9_12'
DC = 'P9_15'
SPI_PORT = 1
SPI_DEVICE = 0

disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

disp.begin()
disp.clear()
disp.display()

width = disp.width
height = disp.height
image = Image.new('1', (width, height))

draw = ImageDraw.Draw(image)

draw.rectangle((0,0,width,height), outline=0, fill=0)

font = ImageFont.load_default()

# Load default font.
font = ImageFont.load_default()
 
# Alternatively load a TTF font.
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
#font = ImageFont.truetype('Minecraftia.ttf', 8)
  
# Write two lines of text.
draw.text((x, top),    'Hello',  font=font, fill=255)
draw.text((x, top+20), 'World!', font=font, fill=255)

# Display image
disp.image(image)
disp.display()


