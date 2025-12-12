from pyconfocal import SCPIController
from pyconfocal import DigitalPin
from pyconfocal import AcquisitionController
from pyconfocal import AcquisitionPort
from pyconfocal import GeneratorPort
from pyconfocal import GeneratorController
import numpy as np
import matplotlib.pyplot as plt
import time
from PIL import Image
from datetime import datetime

"""
Script implementing a very simple way to sweep across all lines

This is only possible for a small image to acquire an entire image in less than 1 seconds.
"""

save = True # set to true to save the captured image

# decimation : length of the buffer in seconds
decimation_dic = {
    1: 1.31072e-4,
    8: 1.048576e-3,
    64: 8.388608e-3,
    1024: 0.134217728,
    8192: 1.073741824,
    65536: 8.589934592
}

decimation = 65536

IP = "Red Pitaya IP address"

image_size = 128

rp_scpi_controller = SCPIController(IP)
trigger_pin = DigitalPin('DIO0_P', rp_scpi_controller)
generator = GeneratorController(rp_scpi_controller)
acquisition_port1 = AcquisitionPort(1, rp_scpi_controller)

acquisition = AcquisitionController(rp_scpi_controller)
acquisition.add_port(acquisition_port1)

# Create generator port objects
gen1 = GeneratorPort(1, rp_scpi_controller)
gen2 = GeneratorPort(2, rp_scpi_controller)

period_slow = decimation_dic[decimation] # width of a pulse in seconds
freq_slow =  1/period_slow # related to the length of the pulse (1/frequency)

period_fast = decimation_dic[decimation]/image_size * 2 # width of a pulse in seconds
freq_fast =  1/period_fast # related to the length of the pulse (1/frequency)

ampl = 1 # amplitude, maximum is 1


# ------ WAVEFORMS -----
points = 16384 # number of total samples, must be this value

# Slow waveform: Create a normalized sawtooth from -1 -> +1 
signal = np.linspace(-1, 1, points) 
data_str_slow = ','.join(f'{x:.5f}' for x in signal) # convert to string

# Fast waveform: Create a normalized triangle -1 -> 1 -> -1
signal1 = np.linspace(-1, 1, int(points/2)) # transition -1 -> 1
signal2 = np.linspace(1, -1, int(points/2)) # transition 1 -> -1
signal = np.hstack([signal1, signal2])
data_str_fast = ','.join(f'{x:.5f}' for x in signal) # convert to string



# ------ GENERATION SET UP ------
# reset generator
generator.reset()
generator.set_debouncer_time(100)

# --- Burst configuration ---
gen1.switch_to_burst_mode()
gen1.set_waveform_number_in_burst(int(image_size/2))
gen1.set_burst_number(1)
gen1.set_burst_period(5000)
gen1.set_default_initial_voltage(-1)
gen1.set_default_last_voltage(-1)

gen2.switch_to_burst_mode()
gen2.set_waveform_number_in_burst(1)
gen2.set_burst_number(1)
gen2.set_burst_period(5000)
gen2.set_default_initial_voltage(-1)
gen2.set_default_last_voltage(-1)


#--- Waveforms ---
gen1.set_waveform(data_str_fast)          # must come before setting type
gen1.set_waveform_type("ARBITRARY")
gen1.set_fequency(freq_fast)
gen1.set_amplitude(ampl)

gen2.set_waveform(data_str_slow)          # must come before setting type
gen2.set_waveform_type("ARBITRARY")
gen2.set_fequency(freq_slow)
gen2.set_amplitude(ampl)

# --- External trigger configuration ---
gen1.set_trigger_mode("EXT_PE")
gen2.set_trigger_mode("EXT_PE")

# activate output
# gen1.enable()
# gen2.enable()
generator.enable() # enable both outputs
time.sleep(1)

# ------ ACQUISITION SET UP ------
# Acquisition settings
acquisition.reset()
acquisition.set_averaging_state('ON')
acquisition.set_decimation(decimation)
acquisition.set_trigger_delay(8192)
acquisition.set_units('RAW')
acquisition.set_debouncer_time(100)
acquisition.set_trigger_mode('EXT_PE')
acquisition.start()

# ----- TRIGGER PIN SET UP -----
trigger_pin.reset_all_pins()
trigger_pin.set_direction('OUT')

# ------ SWEEPING OF LINES -----
start_time = time.time()

# send trigger pulse
trigger_pin.set_high()
trigger_pin.set_low()
print("Trigged!")

# wait for trigger and buffer update
acquisition.wait_for_trigger()
acquisition.wait_for_buffer_update()

buffer = acquisition.get_data_buffer(1)
buffer_min = np.min(buffer)
buffer_max = np.max(buffer)
buffer = 250 * (buffer - buffer_min) / (buffer_max - buffer_min)
print("Line acquired!")

end_time = time.time()
execution_time = end_time - start_time
print(f"Acquitision time: {execution_time} seconds")

# Display full buffer
# plt.plot(buffer)
# plt.ylabel("Counts")
# plt.xlabel("n")
# plt.show()


# Get the current date and time
array_2d = buffer.reshape((image_size, image_size))

# flip odd rows around the center column
odd_lines = array_2d[1::2,:]
flipped_odd_lines = np.flip(odd_lines, axis=1)

flipped_odd_lines = np.roll(flipped_odd_lines, shift=4, axis=1)

array_2d[1::2,:] = flipped_odd_lines

if save:
    # Get the current date and time
    current_time = datetime.now().strftime("%H:%M:%S")
    image_name = f"{current_time}.png"

    pil_img_gray = Image.fromarray(array_2d)
    pil_img_gray = pil_img_gray.convert("L")
    pil_img_gray.save("image.png")
    print("Image saved")

# Display the array as an image with a colormap
# plt.imshow(array_2d[1::2,:], cmap='gray')
# plt.colorbar()
# plt.show()
