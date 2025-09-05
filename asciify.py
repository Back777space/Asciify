import cv2
import argparse
import time
import numpy as np
import array, fcntl, termios

def get_terminal_metrics():
    buf = array.array('H', [0, 0, 0, 0])
    fcntl.ioctl(1, termios.TIOCGWINSZ, buf)
    rows, cols, xpixels, ypixels = buf
    if rows > 0 and cols > 0:
        if xpixels > 0 and ypixels > 0:
            cell_width = xpixels / cols
            cell_height = ypixels / rows
            char_aspect = (cell_height / cell_width) * 0.85
        else:
            char_aspect = 0.55
        return rows, cols, char_aspect
    # defaults
    return 120, 120, 0.55

T_ROWS, T_COLS, T_CHAR_ASPECT = get_terminal_metrics()



def rgb_to_lin(c):
    c = c/255
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4


def luminance(px):
    return 0.2126*rgb_to_lin(px[0]) + 0.7152*rgb_to_lin(px[1]) + 0.0722*rgb_to_lin(px[2])


def perceived_brightness(px):
    l = luminance(px)
    return l*903.3 if l <= 0.008856 else (l**(1/3))*116 - 16


def map_pixel(px):
    pb = perceived_brightness(px)/100
    return BRIGHTNESS_CHARS[int(pb*(len(BRIGHTNESS_CHARS)-1))]


def resize_and_enhance(img):
    h, w = img.shape[:2]
    new_height = T_ROWS
    new_width = int((w / h) * new_height / (1 / T_CHAR_ASPECT))
    resized_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_NEAREST)

    # contrast enhancement
    # enhanced_img = cv2.convertScaleAbs(resized_img, alpha=1.2, beta=0)
    return resized_img


def frame_to_ascii(frame):
    ascii_frame = []
    for row in frame:
        ascii_row = [map_pixel(px) for px in row]
        ascii_frame.append("".join(ascii_row))
    return ascii_frame


def is_image(file_name):
    try:
        with open(file_name, "rb") as f:
            header = f.read(12)
        return (header.startswith(b"\xFF\xD8\xFF") or     # JPG
                header.startswith(b"\x89PNG\r\n\x1a\n") or # PNG
                header.startswith((b"GIF87a", b"GIF89a")) or # GIF
                header.startswith(b"BM") or               # BMP
                header.startswith((b"II*\x00", b"MM\x00*")) or # TIFF
                (header.startswith(b"RIFF") and b"WEBP" in header)) # WEBP
    except OSError:
        return False


def display(img):
    ascii_frame = frame_to_ascii(img)
    print("\033[H")
    print("\n".join(ascii_frame))


def handle_camera():
    cap = cv2.VideoCapture(0)
    fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=False, varThreshold=4)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = resize_and_enhance(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            fgmask = fgbg.apply(frame)
            fgmask_3ch = cv2.merge([fgmask, fgmask, fgmask])
            # frame = cv2.bitwise_and(frame, fgmask_3ch)
            display(frame)
    except KeyboardInterrupt:
        pass
    cap.release()


def handle_img(path):
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = resize_and_enhance(img)
    display(img)


def handle_video(path):
    vidcap = cv2.VideoCapture(path)
    success,img = vidcap.read()
    length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_time = 1/fps
    
    for _ in range(length):
        if not success:
            break
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = resize_and_enhance(img)
        
        start = time.time()
        display(img)
        delta = time.time() - start
        if delta < frame_time:
            time.sleep((frame_time - delta)*0.95)
        success,img = vidcap.read()


def handle_file(path: str):
    if path.split('.')[-1].lower() in ["jpg", "jpeg","png"]:
        handle_img()
    elif path.split('.')[-1].lower() in ["mp4"]:
        handle_video()
    else:
        print("Unsupported file type, exiting...")


if __name__ == "__main__":
    global BRIGHTNESS_CHARS

    parser = argparse.ArgumentParser(
        prog='asciify',
        description='Display anything with ascii characters',
    )
    parser.add_argument("--extended-char-set", required=False, action=argparse.BooleanOptionalAction, default=False)

    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True
    
    camera_subp = subparsers.add_parser("camera")
    file_subp = subparsers.add_parser("file")
    file_subp.add_argument("--path", help="Path to file", required=True)
    
    args = parser.parse_args()

    BRIGHTNESS_CHARS = " .:-=+*#%@"
    if args.extended_char_set:
        BRIGHTNESS_CHARS = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    
    match args.subcommand:
        case "camera":
            handle_camera()
        case "file":
            handle_file(args.path)