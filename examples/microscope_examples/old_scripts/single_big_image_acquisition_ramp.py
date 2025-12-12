from pitaya_confocal.pitaya_confocal import SCPIController
from pitaya_confocal.pitaya_confocal import DigitalPin
from pitaya_confocal.pitaya_confocal import AcquisitionController
from pitaya_confocal.pitaya_confocal import AcquisitionPort
from pitaya_confocal.pitaya_confocal import GeneratorPort
from pitaya_confocal.pitaya_confocal import GeneratorController
import numpy as np
import matplotlib.pyplot as plt
import time
from PIL import Image
from datetime import datetime




"""
Script implementing a very simple way to sweep across all lines in 16 blocks using the scope buffer
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

image_size = 512

rp_scpi_controller = SCPIController(IP)
trigger_pin = DigitalPin('DIO0_P', rp_scpi_controller)
generator = GeneratorController(rp_scpi_controller)
acquisition_port1 = AcquisitionPort(1, rp_scpi_controller)

acquisition = AcquisitionController(rp_scpi_controller)
acquisition.add_port(acquisition_port1)

# Create generator port objects
gen1 = GeneratorPort(1, rp_scpi_controller)
gen2 = GeneratorPort(2, rp_scpi_controller)

period_slow = decimation_dic[decimation] # length of a buffer for decimation
freq_slow =  1/period_slow # related to the length of the pulse (1/frequency)

period_fast = period_slow/32 # width of a pulse in seconds
freq_fast =  1/period_fast # related to the length of the pulse (1/frequency)

ampl = 1 # amplitude, maximum is 1


# ------ WAVEFORMS -----

# fast waveform
# Create a normalized sawtooth from -1 to +1 
points_fast = 16384 # number of total samples, must be this value

signal_fast = np.linspace(-1, 1, points_fast) # transition -1 -> 1
data_str_fast = ','.join(f'{x:.5f}' for x in signal_fast) # convert to string


# slow waveform
points_slow = 16384 * 16
signal_slow = np.linspace(-1, 1, points_slow) # transition -1 -> 1
signal_slow = signal_slow.reshape((16, 16384)) # matrix of slow signal for all 16 blocks

# ------ GENERATION SET UP ------
# reset generator
generator.reset()
generator.set_debouncer_time(100)

# --- Burst configuration ---
gen1.switch_to_burst_mode()
gen1.set_waveform_number_in_burst(32)
gen1.set_burst_number(1)
gen1.set_burst_period(5000)
gen1.set_default_initial_voltage(-1)
gen1.set_default_last_voltage(-1)

gen1.set_waveform(data_str_fast)          # must come before setting type
gen1.set_waveform_type("ARBITRARY")
gen1.set_fequency(freq_fast)
gen1.set_amplitude(ampl)


gen2.switch_to_burst_mode()
gen2.set_waveform_number_in_burst(1)
gen2.set_burst_number(1)
gen2.set_burst_period(5000)
gen2.set_default_initial_voltage(-1)
gen2.set_default_last_voltage(0)


# --- External trigger configuration ---
gen1.set_trigger_mode("EXT_PE")
gen2.set_trigger_mode("EXT_PE")

# activate output
generator.enable() # enable both ports
time.sleep(0.01)


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


# image to save blocks
image_array = np.zeros((512*512))

# ------ SWEEPING OF LINES -----
start_time = time.time()
for i in range(16):
    data_str_slow = ','.join(f'{x:.5f}' for x in signal_slow[i,:])
    gen2.set_waveform(data_str_slow)          # must come before setting type
    gen2.set_waveform_type("ARBITRARY")
    gen2.set_fequency(freq_slow)
    gen2.set_amplitude(ampl)
    gen2.set_default_last_voltage(signal_slow[i,-1])

    # Acquisition settings
    # needs to be done every time to arm the scope
    acquisition.reset()
    acquisition.set_averaging_state('ON')
    acquisition.set_decimation(decimation)
    acquisition.set_trigger_delay(8192)
    acquisition.set_units('RAW')
    acquisition.set_debouncer_time(100)
    acquisition.set_trigger_mode('EXT_PE')
    acquisition.start()
    
    # send trigger pulse
    trigger_pin.set_high()
    trigger_pin.set_low()

    # wait for trigger and buffer update
    acquisition.wait_for_trigger()
    print("trigged")
    acquisition.wait_for_buffer_update()

    buffer = acquisition.get_data_buffer(1)
    print(f"Block {i+1}/16 acquired!")
    image_array[i*16384: (i+1)*16384] = buffer
end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")


# Display full buffer
# plt.plot(buffer)
# plt.ylabel("Counts")
# plt.xlabel("n")
# plt.show()


array_2d = image_array.reshape((image_size, image_size))

if save:
    # Get the current date and time
    current_time = datetime.now().strftime("%H:%M:%S")
    image_name = f"{current_time}.png"

    pil_img_gray = Image.fromarray(array_2d)
    pil_img_gray = pil_img_gray.convert("L")
    pil_img_gray.save("image.png")
    print("Image saved")

# Display the array as an image with a colormap
# plt.imshow(array_2d, cmap='gray')
# plt.colorbar()
# plt.show()
