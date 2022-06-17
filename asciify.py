from PIL import Image, ImageEnhance, ImageOps

brightness_chars = """.`^",:;Il!i><~+_-?][1)(|\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"""

path = input("Enter the path to your image: ")
img = Image.open(path)
# make sure picture is not rotated
img = ImageOps.exif_transpose(img)

def cleanup():
    resize(100)
    add_contrast(1.6)
    img.save("edited.png")

def resize(size):
    global img
    aspect_ratio = img.width/img.height
    # keep w / h ratio and compensate for vertical spacing in terminal 
    new_res = (int(size*aspect_ratio), int(size*0.47))
    img = img.resize(new_res)
    
def add_contrast(factor):
    global img
    img = ImageEnhance.Contrast(img).enhance(factor)

def to_coloured(col):
    return f"\x1b[38;2;{col[0]};{col[1]};{col[2]}m"

def rgb_to_lin(channel):
    linear_px = channel/255
    if linear_px <= 0.04045:
        return linear_px / 12.92
    else:
        return  ((linear_px + 0.055)/1.055)**2.4

def luminance(px):
    return 0.2126 * rgb_to_lin(px[0]) + 0.7152 * rgb_to_lin(px[1]) + 0.0722 * rgb_to_lin(px[2])

# returns value between 0 - 100
def perceived_brightness(px):
    lum = luminance(px)
    if lum <= 0.008856: #216/24389
        return lum * 903.3  #24389/27
    else:
        return (lum ** (1/3)) * 116 - 16

def print_to_console():
    for i in range(img.height):
        for j in range(img.width):
            pixel = img.getpixel((j,i))
            pb = perceived_brightness(pixel)/100
            print(to_coloured(pixel) + brightness_chars[int(pb*(len(brightness_chars)-1))], end="")
        print()

cleanup()
print_to_console()