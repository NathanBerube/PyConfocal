from pyconfocal import ConfocalMicroscope
from .get_ip import get_IP


IP = get_IP()
trigger_pin_name = 'DIO0_P'
waveform_amplitude = 0.5
image_size = 128
decimation = 8192//2

# create microscope object
microscope = ConfocalMicroscope(IP, trigger_pin_name)

microscope.set_image_size(image_size)
microscope.set_decimation(decimation)
microscope.set_waveform_amplitude(waveform_amplitude)

# reset and configure the function generator of the microscope
# reset and configure acquisition module of the microscope
microscope.intialize()

# start continuous acquisition
microscope.continuous_acquisition()