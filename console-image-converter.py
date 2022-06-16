from PIL import Image, ImageEnhance, ImageOps

brightness_chars = """$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1[]?-_+~<>i!lI;:,"^`."""
mapping_factor = 255/(len(brightness_chars) - 1)

path = input("Enter the path to your image: ")
img = Image.open(path)
img = ImageOps.exif_transpose(img)

def clean_pic(contrast):
    resize()
    add_contrast(contrast)
    img.save("new.png")

def resize():
    global h
    global w
    global img
    h, w = img.height, img.width
    while h >= 70 and w >= 70:
        new_size = (int(w/2), int(h/2))
        img = img.resize(new_size)
        w, h = new_size
    
def add_contrast(scale):
    global img
    img = ImageEnhance.Contrast(img).enhance(scale)

def print_to_console():
    for i in range(h):
        for j in range(w):
            pixel = img.getpixel((j,i))
            
            avg = sum(pixel) / len(pixel)
            if (avg > 5 and avg < 250):
                print(brightness_chars[int(avg/mapping_factor)], end="")
            else:
                print(" ", end="")
        print()

clean_pic(1.25)
print_to_console()