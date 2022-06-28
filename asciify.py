from PIL import Image, ImageEnhance
import cv2
import os
import shutil
from time import sleep

BRIGHTNESS_CHARS = """ .,`:;^+*_?)(\/Y0H%S#@"""
NEW_SIZE = 120
CONTRAST_FACTOR = 1.75
FPS_FACTOR = 680

def cleanup():
    resize(NEW_SIZE)
    add_contrast(CONTRAST_FACTOR) # add contrast to make colour differences more prominent

def resize(size):
    global img
    aspect_ratio = img.width/img.height
    # keep w / h ratio and compensate for vertical spacing in terminal 
    new_res = (int(size*aspect_ratio), int(size*0.45))
    img = img.resize(new_res)
    
def add_contrast(factor):
    global img
    img = ImageEnhance.Contrast(img).enhance(factor)

def rgb_to_lin(channel):
    linear_px = channel/255
    if linear_px <= 0.04045:
        return linear_px / 12.92
    return  ((linear_px + 0.055)/1.055)**2.4

def luminance(px):
    return 0.2126 * rgb_to_lin(px[0]) + 0.7152 * rgb_to_lin(px[1]) + 0.0722 * rgb_to_lin(px[2])

# returns value between 0 - 100
def perceived_brightness(px):
    lum = luminance(px)
    if lum <= 0.008856: #216/24389
        return lum * 903.3  #24389/27
    return (lum ** (1/3)) * 116 - 16

# converts img to ascii + writes to txt file
def write(count=0):
    with open(f"asciiFrames/frame{count}.txt", 'w') as f:
        for i in range(img.height):
            for j in range(img.width):
                pixel = img.getpixel((j,i))
                pb = perceived_brightness(pixel)/100
                # map pb value to corresponding brightness character
                f.write(BRIGHTNESS_CHARS[int(pb*(len(BRIGHTNESS_CHARS)-1))])
            f.write('\n')
        
def print_to_console(fps=0, count=1):
    frame = ""
    for file_num in range(count):
        with open(f"asciiFrames/frame{file_num}.txt", 'r') as f:
            frame = f.read()
        print(frame, end='')
        # display with correct fps rate
        sleep(fps/FPS_FACTOR)
        #make space for next frame
        print("\r")

# returns total saved frames
def save_frames(vid):   
    global img
    success,img = vid.read()
    count = 0
    # read every frame
    while success:
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        cleanup()
        write(count)
        success,img = vid.read()
        count += 1
    return count

def handle_pic():
    global img
    img = Image.open(path)
    cleanup()
    write()
    print_to_console()

def handle_vid():
    vidcap = cv2.VideoCapture(path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_count = save_frames(vidcap)
    print_to_console(fps, frame_count)

if __name__ == "__main__":
    path = input("Enter the path to your file: ")
    # delete full directory if it exists and make a new one
    if os.path.isdir("asciiFrames"):
        shutil.rmtree("asciiFrames")
    os.mkdir("asciiFrames")
    if path.split('.')[-1] in ["jpg", "jpeg","png","JPG"]:
        handle_pic()

    elif path.split('.')[-1] in ["mp4", "MP4"]:
        handle_vid()

    else:
        print("Invalid file")