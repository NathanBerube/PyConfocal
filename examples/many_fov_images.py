from pyconfocal import ConfocalMicroscope
from PIL import Image
from datetime import datetime
from os.path import join
"""
This code is doing a sweep of the FOV ratio of the microscope going from 10 % to 100 % of it.
An image is acquired for each FOV and is saved at a specified saving path on your computer

The Red Pitaya IP address can be found on the web GUI of the Red Pitaya afte activating the SCPI
server.

This code was tested on a StemLab 125-14 Red Pitaya.

December 15 2025
Nathan Bérubé
"""

saving_path = "" # add your saving path
IP = '' # add your red pitaya IP address

trigger_pin_name = 'DIO0_P' # external trigger pin of the Red Pitaya
fov_ratio_array = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0] # sweeping of the fov of the microscope
image_size = 128 # size of the image in pixels (128, 512 and 1024 are supported)
decimation = 8192 # decimation of the Red pitaya clock, controls the speed of the galvos

# create microscope object
microscope = ConfocalMicroscope(IP, trigger_pin_name)

# set parameters
microscope.set_image_size(image_size)
microscope.set_decimation(decimation)

# looping on all fovs...
for fov_ratio in fov_ratio_array:

    # set fov value
    microscope.set_fov_ratio(fov_ratio)

    # reset and configure the function generator of the microscope
    # reset and configure acquisition module of the microscope
    # initialize the microscope with new fov ratio
    microscope.intialize()

    # get an image
    image = microscope.acquire_image()

    # save image
    # get the current date and time for image name
    current_time = datetime.now().strftime("%H_%M_%S_%f")
    image_name = f"image{current_time}_fov_{fov_ratio}.png"

    # convert image to grayscale png
    pil_img_gray = Image.fromarray(image)
    pil_img_gray = pil_img_gray.convert("L")
    pil_img_gray.save(join(saving_path, image_name))
    print(f"Image saved at {join(saving_path, image_name)}")

microscope.reset_settings() # reset settings for next acquisition
