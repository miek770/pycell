#-*- coding: utf-8 -*-

import time, sys
from datetime import datetime
from SSD1306 import SSD1306
from PIL import Image, ImageDraw, ImageFont

batt = 0.7

def popup(message, image, linelength=20, padding=3, font=ImageFont.load_default()):

    from textwrap import wrap

    width, heigh = image.size
    draw = ImageDraw.Draw(image)
    message = wrap(message, width=linelength)

    largest = 0
    highest = 0
    for l in message:
        w = font.getsize(l)
        if w[0] > largest:
            largest = w[0]
        if w[1] > highest:
            highest = w[1]

    draw.rectangle(((width - largest)/2 - padding,
                    (height - len(message)*highest)/2 - padding,
                    (width + largest - 1)/2 + padding,
                    (height + len(message)*highest - 1)/2 + padding
                   ),
                   outline=255,
                   fill=0)

    line = 0
    for l in message:
        draw.text(((width - largest)/2,
                   (height - len(message)*highest)/2 + line*highest
                  ),
                  l,
                  font=font,
                  fill=255)
        line += 1

    return image

disp = SSD1306(rst='J4.12', dc='J4.14', cs='J4.11')

# Initialize library
disp.begin()

# Clear display
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
 
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
  
# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = 2
shape_width = 20
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = padding
# Draw an ellipse.
draw.ellipse((x, top , x+shape_width, bottom), outline=255, fill=0)
x += shape_width+padding
# Draw a rectangle.
draw.rectangle((x, top, x+shape_width, bottom), outline=255, fill=0)
x += shape_width+padding
# Draw a triangle.
draw.polygon([(x, bottom), (x+shape_width/2, top), (x+shape_width, bottom)], outline=255, fill=0)
x += shape_width+padding
# Draw an X.
draw.line((x, bottom, x+shape_width, top), fill=255)
draw.line((x, top, x+shape_width, bottom), fill=255)
x += shape_width+padding

# Load default font.
#font = ImageFont.load_default()
font = ImageFont.truetype('../ressources/Minecraftia-Regular.ttf', 8)

# Write two lines of text.
draw.text((x, top),    'Hello',  font=font, fill=255)
draw.text((x, top+20), 'World!', font=font, fill=255)

# Indique la date / heure en haut à gauche
#==========================================

# Sur 1 ligne
date = datetime.strftime(datetime.now(), "%y-%m-%d %H:%M:%S")
draw.text((0, 0), date, font=font, fill=255)

# Indique le niveau de batterie en haut à droite
#================================================
batt_size = 13, 6

# Enveloppe batterie
draw.rectangle((width - (batt_size[0] - 1),
                0,
                width - 1,
                batt_size[1] - 1
               ),
               outline=255,
               fill=0)

draw.rectangle((width-batt_size[0],
                1,
                width-batt_size[0],
                batt_size[1] - 2
               ),
               outline=255,
               fill=0)

# Niveau de charge
draw.rectangle((width-(batt_size[0] - 2),
                1,
                width-(batt_size[0] - 2) + batt*(batt_size[0] - 3),
                batt_size[1] - 2
               ),
               outline=255,
               fill=255)

image = popup(u"Ceci est un test, qui fonctionne plutôt bien!", image, font=font)

# Display image.
disp.image(image)
disp.display()

print "Done!"
