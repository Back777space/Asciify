from PIL import Image, ImageEnhance, ImageOps
from termcolor import colored

brightness_chars = """$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1[]?-_+~<>i!lI;:,"^`."""
mapping_factor = 255/(len(brightness_chars) - 1)

path = input("Enter the path to your image: ")
img = Image.open(path)
# make sure picture is not rotated
img = ImageOps.exif_transpose(img)

def cleanup():
    resize(50)
    add_contrast(1.9)
    #img.save("edited.png")

def resize(size):
    global img
    aspect_ratio = img.width/img.height
    new_res = (int(size*aspect_ratio), size)
    img = img.resize(new_res)
    
def add_contrast(scale):
    global img
    img = ImageEnhance.Contrast(img).enhance(scale)

def to_coloured(col):
    return f"\x1b[38;2;{col[0]};{col[1]};{col[2]}m"

def print_to_console():
    for i in range(img.height):
        for j in range(img.width):
            pixel = img.getpixel((j,i))
            avg = sum(pixel) / len(pixel)
            if (avg != 255 and avg > 5):
                print(brightness_chars[int(avg/mapping_factor)], end="")
            else:
                print(" ", end="")
        print()

cleanup()
print_to_console()