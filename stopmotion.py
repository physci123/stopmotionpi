#!/usr/bin/env python
from picamera import PiCamera
from PIL import Image, ImageTk
from guizero import App, Box, Picture, Text, PushButton
import tkinter as tki
from gpiozero import Button
from io import BytesIO
from time import strftime
import numpy as np
import threading

button = Button(17)
camera = PiCamera(resolution="640x480")

def update_preview_image():
    global preview_pic
    image = np.empty((480, 640, 3), dtype=np.uint8)
    for _ in camera.capture_continuous(image, 'rgb', use_video_port=True):
        img = Image.fromarray(image)
        img = ImageTk.PhotoImage(image=img)
        preview_pic.configure(image=img)
        preview_pic.image = img
                
def check_button():
    while True:
        button.wait_for_press()
        take_picture()

#take_picture
def take_picture():
    take_img_btn.disable()
    app.tk.update()
    # capture the image
    pic_stream = BytesIO()
    camera.capture(pic_stream, format='jpeg')
    pic_stream.seek(0)
    # append the camera image to the list
    app.images.append(Image.open(pic_stream))
    update_app()

def del_last_pic():
    app.images.pop()
    update_app()

def reset_arr():
    app.images = []
    update_app()

def save_movie():
    save_btn.disable()
    reset_btn.disable()
    del_last_btn.disable()
    take_img_btn.disable()
    app.tk.update()
    app.images[0].save('./animation_{}.gif'.format(strftime("%Y%m%d%H%M%S")),
    save_all=True, append_images=app.images[1:], optimize=False, duration=250,loop=0)
    save_btn.enable()
    reset_btn.enable()
    del_last_btn.enable()
    take_img_btn.enable()

def update_app():
    if len(app.images) == 0:
        save_btn.disable()
        reset_btn.disable()
        del_last_btn.disable()
    else:
        save_btn.enable()
        reset_btn.enable()
        del_last_btn.enable()
        take_img_btn.enable()
    ii = 0
    while ii < 5:
        offset = 0 if len(app.images) - 5 < 0 else len(app.images) - 5
        if ii < len(app.images):
            last_pics[ii].image = app.images[ii + offset]
            last_pics[ii].show()
        else:
            last_pics[ii].image = None
            last_pics[ii].hide()
        ii += 1
        
def on_close():
    camera.close()
    exit()
        
app = App(title="Stop Motion Pi", width=800, height=500)
app.when_closed = on_close
button_box = Box(app, layout="grid")
picture_box = Box(app, layout="grid")

take_img_btn = PushButton(button_box, text="take picture", command=take_picture, grid=[0,0])
del_last_btn = PushButton(button_box, text="delete Last Picture", command=del_last_pic, grid=[1,0])
reset_btn = PushButton(button_box, text="Start Again", command=reset_arr, grid=[2,0])
save_btn = PushButton(button_box, text="Create Movie", command=save_movie, grid=[3,0])

pic_pic_box = Box(picture_box, grid=[0,0], width = 640, height = 480)
preview_pic = tki.Label(pic_pic_box.tk)
pic_pic_box.add_tk_widget(preview_pic)

last_pic_box = Box(picture_box, layout="grid", grid=[1,0], width = 128, height = 480)

last_pics = []

for ii in range(5):
    last_pics.append(Picture(last_pic_box, grid=[0,ii], width = 128, height = 96))

app.images = []

thread_button = threading.Thread(target=check_button)
thread_button.start()

thread_preview = threading.Thread(target=update_preview_image)
thread_preview.start()

update_app()

app.display()
