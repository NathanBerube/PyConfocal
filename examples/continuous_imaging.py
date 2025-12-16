from pyconfocal import ConfocalMicroscope

"""
This code is used to show a window displaying images in real-time during acquisition (continuous acquisition mode). This script can be used
for alignment of the sample before saving images. The images are NOT saved in continuous acquisition mode.

The Red Pitaya IP address can be found on the web GUI of the Red Pitaya after activating the SCPI
server.

This code was tested on a StemLab 125-14 Red Pitaya.

December 15 2025
Nathan Bérubé
"""

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

# start continuous acquisition
# a window will open showing the images
microscope.continuous_acquisition()

# por