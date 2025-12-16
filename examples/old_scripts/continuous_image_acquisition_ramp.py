from pyconfocal import SCPIController
from pyconfocal import DigitalPin
from pyconfocal import AcquisitionController
from pyconfocal import AcquisitionPort
from pyconfocal import GeneratorPort
from pyconfocal import GeneratorController
import numpy as np
import matplotlib.pyplot as plt
import time

"""
Script implementing a very simple way to sweep across all lines

This is only possible for a small image to acquire an entire image in less than 1 seconds.

Continous acquisition mode with ramp waveforms.

** The script continuous_imaging.py should be used instead. This code was written before developing 
the ConfocalMicroscope class. ***
"""

IP = "Red Pitaya IP address"

# decimation : length of the buffer in seconds
decimation_dic = {
    1: 1.31072e-4,
    8: 1.048576e-3,
    64: 8.388608e-3,
    1024: 0.134217728,
    8192: 1.073741824,
    65536: 8.589934592
}

decimation = 8192

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

period_fast = decimation_dic[decimation]/image_size # width of a pulse in seconds
freq_fast =  1/period_fast # related to the length of the pulse (1/frequency)

ampl = 0.1 # amplitude, maximum is 1


# ------ WAVEFORMS -----
# Create a normalized sawtooth from -1 to +1
points = 16384 # number of total samples, must be this value

signal = np.linspace(-1, 1, points) # transition -1 -> 1
data_str = ','.join(f'{x:.5f}' for x in signal) # convert to string



# ------ GENERATION SET UP ------
# reset generator
generator.reset()
generator.set_debouncer_time(100)

# --- Burst configuration ---
gen1.switch_to_burst_mode()
gen1.set_waveform_number_in_burst(image_size)
gen1.set_burst_number(1)
gen1.set_burst_period(5000)

gen2.switch_to_burst_mode()
gen2.set_waveform_number_in_burst(1)
gen2.set_burst_number(1)
gen2.set_burst_period(5000)

#--- Waveforms ---
gen1.set_waveform(data_str)          # must come before setting type
gen1.set_waveform_type("ARBITRARY")
gen1.set_fequency(freq_fast)
gen1.set_amplitude(ampl)
gen1.set_default_initial_voltage(-ampl)
gen1.set_default_last_voltage(-ampl)

gen2.set_waveform(data_str)          # must come before setting type
gen2.set_waveform_type("ARBITRARY")
gen2.set_fequency(freq_slow)
gen2.set_amplitude(ampl)
gen2.set_default_initial_voltage(-ampl)
gen2.set_default_last_voltage(-ampl)

# --- External trigger configuration ---
gen1.set_trigger_mode("EXT_PE")
gen2.set_trigger_mode("EXT_PE")

# activate output
generator.enable()
time.sleep(0.1)

# ------ ACQUISITION SET UP ------
# Acquisition settings
acquisition.reset()
# acquisition.set_averaging_state('ON')
acquisition.set_decimation(decimation)
acquisition.set_trigger_delay(8192)
acquisition.set_units('RAW')
acquisition.set_debouncer_time(100)
acquisition.set_trigger_mode('EXT_PE')
acquisition.start()

# ----- TRIGGER PIN SET UP -----
trigger_pin.reset_all_pins()
trigger_pin.set_direction('OUT')


# ---- LIVE PLOTTING -----
plt.ion()                         # enable interactive mode

fig = plt.figure()                # <- create exactly one figure
ax = fig.add_subplot(111)         # <- avoid plt.subplots()

img = np.zeros((image_size, image_size))
img_handle = ax.imshow(img, cmap='gray', vmin=0, vmax=255)

# IMPORTANT: attach colorbar explicitly to the figure
fig.colorbar(img_handle, ax=ax)

fig.canvas.draw()
fig.canvas.flush_events()

i = 0
while True:
    try:
        acquisition.set_trigger_mode('EXT_PE') # arm acquisition again
        acquisition.start()

        # Trigger acquisition
        trigger_pin.set_high()
        time.sleep(0.001)
        trigger_pin.set_low()

        acquisition.wait_for_trigger()
        acquisition.wait_for_buffer_update()
        buffer = acquisition.get_data_buffer(1)
        buffer_min = np.min(buffer)
        buffer_max = np.max(buffer)
        buffer = 250 * (buffer - buffer_min) / (buffer_max - buffer_min)

        try:
            frame = buffer.reshape((image_size, image_size))
        except ValueError:
            print("Buffer not the right size:", len(buffer))
            continue

        img_handle.set_data(frame.T)

        # Fastest and safest way to refresh WITHOUT opening new windows:
        fig.canvas.draw_idle()
        fig.canvas.flush_events()
        ax.set_title(f"Frame {i}")

        # Optional throttle
        time.sleep(0.01)
        i+=1

    except KeyboardInterrupt:
        print("\n Stopped by user (Ctrl+C)")