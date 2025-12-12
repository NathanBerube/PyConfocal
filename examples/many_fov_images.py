from pyconfocal import ConfocalMicroscope
from PIL import Image
from datetime import datetime
from os.path import join


saving_path = "" # add your saving path
IP = '' # add your red pitaya IP address

trigger_pin_name = 'DIO0_P'
fov_ratio_array = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
image_size = 512
decimation = 8192//4

# create microscope object
microscope = ConfocalMicroscope(IP, trigger_pin_name)

microscope.set_image_size(image_size)
microscope.set_decimation(decimation)

for fov_ratio in fov_ratio_array:
    microscope.set_fov_ratio(fov_ratio)

    # reset and configure the function generator of the microscope
    # reset and configure acquisition module of the microscope
    microscope.intialize()

    # get an image
    image = microscope.acquire_image()

    # save image
    # get the current date and time for image name
    current_time = datetime.now().strftime("%H_%M_%S_%f")
    # image_name = f"calibration_fov_488nm_{waveform_amplitude*100}_dec_{decimation}.png"
    image_name = f"rhizhome_488nm_fov_{fov_ratio}.png"

    # convert image to grayscale png
    pil_img_gray = Image.fromarray(image)
    pil_img_gray = pil_img_gray.convert("L")
    pil_img_gray.save(join(saving_path, image_name))
    print(f"Image saved at {join(saving_path, image_name)}")

microscope.reset_settings()
