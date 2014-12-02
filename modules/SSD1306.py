# This is an extract from https://github.com/adafruit/Adafruit_Python_SSD1306
# which is meant to be used for the Arietta G25 from Acmesystems over SPI.
# The code will use https://github.com/tanzilli/ablib instead of Adafruit's IO librairies and skip the parts about I2C.
#
# It is not meant to be merged back into Adafruit's base project.
#
# ---
#
# copyright (c) 2014 adafruit industries
# author: tony dicola
#
# permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "software"), to deal
# in the software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the software, and to permit persons to whom the software is
# furnished to do so, subject to the following conditions:
#
# the above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the software.
#
# the software is provided "as is", without warranty of any kind, express or
# implied, including but not limited to the warranties of merchantability,
# fitness for a particular purpose and noninfringement. in no event shall the
# authors or copyright holders be liable for any claim, damages or other
# liability, whether in an action of contract, tort or otherwise, arising from,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import logging
import time

# For the Arietta GPIO
from ablib import Pin

# For the Arietta SPI
import posix
import struct
from ctypes import addressof, create_string_buffer, sizeof, string_at
from fcntl import ioctl
from spi_ctypes import *

# Constants
SSD1306_SETCONTRAST = 0x81
SSD1306_DISPLAYALLON_RESUME = 0xA4
SSD1306_DISPLAYALLON = 0xA5
SSD1306_NORMALDISPLAY = 0xA6
SSD1306_INVERTDISPLAY = 0xA7
SSD1306_DISPLAYOFF = 0xAE
SSD1306_DISPLAYON = 0xAF
SSD1306_SETDISPLAYOFFSET = 0xD3
SSD1306_SETCOMPINS = 0xDA
SSD1306_SETVCOMDETECT = 0xDB
SSD1306_SETDISPLAYCLOCKDIV = 0xD5
SSD1306_SETPRECHARGE = 0xD9
SSD1306_SETMULTIPLEX = 0xA8
SSD1306_SETLOWCOLUMN = 0x00
SSD1306_SETHIGHCOLUMN = 0x10
SSD1306_SETSTARTLINE = 0x40
SSD1306_MEMORYMODE = 0x20
SSD1306_COLUMNADDR = 0x21
SSD1306_PAGEADDR = 0x22
SSD1306_COMSCANINC = 0xC0
SSD1306_COMSCANDEC = 0xC8
SSD1306_SEGREMAP = 0xA0
SSD1306_CHARGEPUMP = 0x8D
SSD1306_EXTERNALVCC = 0x1
SSD1306_SWITCHCAPVCC = 0x2

# Scrolling constants
SSD1306_ACTIVATE_SCROLL = 0x2F
SSD1306_DEACTIVATE_SCROLL = 0x2E
SSD1306_SET_VERTICAL_SCROLL_AREA = 0xA3
SSD1306_RIGHT_HORIZONTAL_SCROLL = 0x26
SSD1306_LEFT_HORIZONTAL_SCROLL = 0x27
SSD1306_VERTICAL_AND_RIGHT_HORIZONTAL_SCROLL = 0x29
SSD1306_VERTICAL_AND_LEFT_HORIZONTAL_SCROLL = 0x2A

class spibus():
    """Class provided in Acme Systems' playground examples spisend.py.
    """

    fd=None
    write_buffer = create_string_buffer(8192)
    read_buffer = create_string_buffer(8192)

    ioctl_arg = spi_ioc_transfer(tx_buf=addressof(write_buffer),
                                 rx_buf=addressof(read_buffer),
                                 len=1,
                                 delay_usecs=0,
                                 speed_hz=5000000,
                                 bits_per_word=8,
                                 cs_change = 0)

    def __init__(self, device, cs):
        self._cs = Pin(cs, 'HIGH')
        self.fd = posix.open(device, posix.O_RDWR)
        ioctl(self.fd, SPI_IOC_RD_MODE, " ")
        ioctl(self.fd, SPI_IOC_WR_MODE, struct.pack('I',0))

    def send(self, len):
        self._cs.low()
        self.ioctl_arg.len=len
        ioctl(self.fd, SPI_IOC_MESSAGE(1), addressof(self.ioctl_arg))
        self._cs.high()

    def write(self, s):
        i = 0
        for c in s:
            if c.__class__ is not str:
                c = chr(c)
            self.write_buffer[i] = c
            i += 1
        self.send(len(s))

class SSD1306():

    def __init__(self, rst, dc, cs, spi="/dev/spidev32766.0"):
        self._log = logging.getLogger('Adafruit_SSD1306.SSD1306Base')
        self.width = 128
        self.height = 64
        self._pages = self.height/8
        self._buffer = [0]*(self.width*self._pages)

        # Setup reset, DC and CS pins
        self._rst = Pin(rst, 'HIGH')
        self._dc = Pin(dc, 'HIGH')

        # Handle hardware SPI
        self._log.debug('Using hardware SPI')
        self._spi = spibus(spi, cs)

    def _initialize(self):
        # 128x64 pixel specific initialization.
        self.command(SSD1306_DISPLAYOFF)                    # 0xAE
        self.command(SSD1306_SETDISPLAYCLOCKDIV)            # 0xD5
        self.command(0x80)                                  # the suggested ratio 0x80
        self.command(SSD1306_SETMULTIPLEX)                  # 0xA8
        self.command(0x3F)
        self.command(SSD1306_SETDISPLAYOFFSET)              # 0xD3
        self.command(0x0)                                   # no offset
        self.command(SSD1306_SETSTARTLINE | 0x0)            # line #0
        self.command(SSD1306_CHARGEPUMP)                    # 0x8D
        if self._vccstate == SSD1306_EXTERNALVCC:
            self.command(0x10)
        else:
            self.command(0x14)
        self.command(SSD1306_MEMORYMODE)                    # 0x20
        self.command(0x00)                                  # 0x0 act like ks0108
        self.command(SSD1306_SEGREMAP | 0x1)
        self.command(SSD1306_COMSCANDEC)
        self.command(SSD1306_SETCOMPINS)                    # 0xDA
        self.command(0x12)
        self.command(SSD1306_SETCONTRAST)                   # 0x81
        if self._vccstate == SSD1306_EXTERNALVCC:
            self.command(0x9F)
        else:
            self.command(0xCF)
        self.command(SSD1306_SETPRECHARGE)                  # 0xd9
        if self._vccstate == SSD1306_EXTERNALVCC:
            self.command(0x22)
        else:
            self.command(0xF1)
        self.command(SSD1306_SETVCOMDETECT)                 # 0xDB
        self.command(0x40)
        self.command(SSD1306_DISPLAYALLON_RESUME)           # 0xA4
        self.command(SSD1306_NORMALDISPLAY)                 # 0xA6

    def command(self, c):
        """Send command byte to display. D/C low = Command."""
        # SPI write.
        self._dc.low()
        self._spi.write([c])

    def data(self, c):
        """Send byte of data to display. D/C high = Data."""
        self._dc.high()
        self._spi.write([c])

    def begin(self, vccstate=SSD1306_SWITCHCAPVCC):
        """Initialize display."""
        # Save vcc state.
        self._vccstate = vccstate
        # Reset and initialize display.
        self.reset()
        self._initialize()
        # Turn on the display.
        self.command(SSD1306_DISPLAYON)

    def reset(self):
        """Reset the display."""
        # Set reset high for a millisecond.
        self._rst.high()
        time.sleep(0.001)
        # Set reset low for 10 milliseconds.
        self._rst.low()
        time.sleep(0.010)
        # Set reset high again.
        self._rst.high()

    def display(self):
        """Write display buffer to physical display."""
        self.command(SSD1306_COLUMNADDR)
        self.command(0)              # Column start address. (0 = reset)
        self.command(self.width-1)   # Column end address.
        self.command(SSD1306_PAGEADDR)
        self.command(0)              # Page start address. (0 = reset)
        self.command(self._pages-1)  # Page end address.

        # Write buffer data.
        # Set DC high for data.
        self._dc.high()
        # Write buffer.
        self._spi.write(self._buffer)

    def image(self, image):
        """Set buffer to value of Python Imaging Library image.  The image should
        be in 1 bit mode and a size equal to the display size.
        """
        if image.mode != '1':
            raise ValueError('Image must be in mode 1.')
        imwidth, imheight = image.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError('Image must be same dimensions as display ({0}x{1}).'.format(self.width, self.height))
        # Grab all the pixels from the image, faster than getpixel.
        pix = image.load()
        # Iterate through the memory pages
        index = 0
        for page in range(self._pages):
            # Iterate through all x axis columns.
            for x in range(self.width):
                # Set the bits for the column of pixels at the current position.
                bits = 0
                # Don't use range here as it's a bit slow
                for bit in [0, 1, 2, 3, 4, 5, 6, 7]:
                    bits = bits << 1
                    bits |= 0 if pix[(x, page*8+7-bit)] == 0 else 1
                # Update buffer byte and increment to next byte.
                self._buffer[index] = bits
                index += 1

    def clear(self):
        """Clear contents of image buffer."""
        self._buffer = [0]*(self.width*self._pages)

    def set_contrast(self, contrast):
        """Sets the contrast of the display.  Contrast should be a value between
        0 and 255."""
        if contrast < 0 or contrast > 255:
            raise ValueError('Contrast must be a value from 0 to 255 (inclusive).')
        self.command(SSD1306_SETCONTRAST)
        self.command(contrast)

    def dim(self, dim):
        """Adjusts contrast to dim the display if dim is True, otherwise sets the
        contrast to normal brightness if dim is False.
        """
        # Assume dim display.
        contrast = 0
        # Adjust contrast based on VCC if not dimming.
        if not dim:
            if self._vccstate == SSD1306_EXTERNALVCC:
                contrast = 0x9F
            else:
                contrast = 0xCF

