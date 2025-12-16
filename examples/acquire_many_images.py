from pyconfocal import ConfocalMicroscope
from PIL import Image
from datetime import datetime
from os.path import join
"""
This code is used to acquire many images with the same acquisition parameters. The microscope
is initialized before acquiring an image stack.

The Red Pitaya IP address can be found on the web GUI of the Red Pitaya afte activating the SCPI
server.

This code was tested on a StemLab 125-14 Red Pitaya.

December 15 2025
Nathan Bérubé
"""

saving_path = "" # add your saving path
IP = '' # add your red pitaya IP address

trigger_pin_name = 'DIO0_P' # external trigger pin of the Red Pitaya
fov_ratio  = 0.5 # fov ratio for the sweeping (1 is full fov)
n_images = 10 # number of images to acquire
image_size = 128 # size of the image in pixels (128, 512 and 1024 are supported)
decimation = 8192 # decimation of the Red pitaya clock, controls the speed of the galvos

# create microscope object
microscope = ConfocalMicroscope(IP, trigger_pin_name)

# set parameters
microscope.set_image_size(image_size)
microscope.set_decimation(decimation)
microscope.set_fov_ratio(fov_ratio)

# reset and configure the function generator of the microscope
# reset and configure acquisition module of the microscope
# initialize microscope with specified acquisition parameters
microscope.intialize()

# get a stack of n_images stack
image_stack = microscope.acquire_many_images(n_images)

# save each image
# get the current date and time for image name
for i in range(n_images):
    current_time = datetime.now().strftime("%H_%M_%S_%f")
    image_name = f"{current_time}.png"

    # convert image to grayscale png
    pil_img_gray = Image.fromarray(image_stack[i,...])
    pil_img_gray = pil_img_gray.convert("L")
    pil_img_gray.save(join(saving_path, image_name))
    print(f"Image saved at {join(saving_path, image_name)}")

microscope.reset_settings() # reset settings for next acquisition