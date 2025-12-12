from pyconfocal import ConfocalMicroscope
from .get_ip import get_IP
from PIL import Image
from datetime import datetime
from os.path import join

saving_path = "/Users/nathan/Downloads"
IP = get_IP()
trigger_pin_name = 'DIO0_P'
waveform_amplitude = 0.5
n_images = 10
image_size = 128
decimation = 8192

# create microscope object
microscope = ConfocalMicroscope(IP, trigger_pin_name)

microscope.set_image_size(image_size)
microscope.set_decimation(decimation)
microscope.set_waveform_amplitude(waveform_amplitude)

# reset and configure the function generator of the microscope
# reset and configure acquisition module of the microscope
microscope.intialize()

# get image stack of 10
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
