from pyconfocal import ConfocalMicroscope


IP = '' # add your red pitaya IP address

trigger_pin_name = 'DIO0_P'
fov_ratio = 0.5
image_size = 128
decimation = 8192//2

# create microscope object
microscope = ConfocalMicroscope(IP, trigger_pin_name)

microscope.set_image_size(image_size)
microscope.set_decimation(decimation)
microscope.set_fov_ratio(fov_ratio)

# reset and configure the function generator of the microscope
# reset and configure acquisition module of the microscope
microscope.intialize()

# start continuous acquisition
microscope.continuous_acquisition()