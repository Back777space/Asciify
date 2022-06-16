from PIL import Image, ImageEnhance, ImageOps

brightness_chars = """$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1[]?-_+~<>i!lI;:,"^`."""

path = input("Enter the path to your image: ")
img = Image.open(path)
# make sure picture is not rotated
img = ImageOps.exif_transpose(img)

def cleanup():
    resize(100)
    add_contrast(1.6)
    #img.save("edited.png")

def resize(size):
    global img
    aspect_ratio = img.width/img.height
    # keep w / h ratio and compensate for vertical spacing in terminal 
    new_res = (int(size*aspect_ratio), int(size*0.5))
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

def print_to_console():
    for i in range(img.height):
        for j in range(img.width):
            pixel = img.getpixel((j,i))
            lum = luminance(pixel)
            if (lum > 0.02 and lum < 0.97):
                print(to_coloured(pixel) + brightness_chars[int(lum*len(brightness_chars))], end="")
            else:
                print(" ", end="")
        print()

cleanup()
print_to_console()