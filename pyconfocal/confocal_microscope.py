from .scpi_controller import SCPIController
from .digital_pin import DigitalPin
from .acquisition_controller import AcquisitionController
from .acquisition_port import AcquisitionPort
from .generator_port import GeneratorPort
from .generator_controller import GeneratorController
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from tqdm import tqdm

class ConfocalMicroscope:
    """
    Controller for a confocal scanning microscope based on a
    Red Pitaya device. This class abstracts:

    - Generator configuration (fast and slow scanning axes)
    - Acquisition setup and synchronization
    - Trigger handling through a digital pin
    - Arbitrary waveform generation for galvo scanning
    - Automated image acquisition (single or multiple)

    The class ensures proper synchronization between waveform generation
    and acquisition to performframe scans.
    """

    def __init__(self, red_pitaya_ip: str, trigger_pin_name: str) -> None:
        """
        Initialize the confocal microscope system.

        Parameters
        ----------
        red_pitaya_ip : str
            IP address of the Red Pitaya board.
        trigger_pin_name : str
            Name of the digital pin used for external triggering.
        """
        self.scpi_controller = SCPIController(red_pitaya_ip)

        self.trigger_pin = DigitalPin(trigger_pin_name, self.scpi_controller)
        self.trigger_pin.reset_all_pins()
        self.trigger_pin.set_direction('OUT')

        self.generator = GeneratorController(self.scpi_controller)
        self.fast_port = GeneratorPort(1, self.scpi_controller)
        self.slow_port = GeneratorPort(2, self.scpi_controller)

        self.acquisition = AcquisitionController(self.scpi_controller)
        self.acquisition.add_port(AcquisitionPort(1, self.scpi_controller))

        self.image_size = 128
        self.decimation = 8192
        self.amplitude = 0.5
        self.buffer_size = 16384

    def set_decimation(self, decimation: int) -> None:
        """"
        Set the decimation factor of the RedPitaya clock

        Parameters
        ----------
        decimation : int
            Decimation factor applied to the ADC sampling clock.
            Must be one of ``[1, 2, 4, 8, 16]`` or any integer between
            ``17`` and ``65 536`` (inclusive). Values outside this range raise
            a ``ValueError``.

        Raises
        ------
        TypeError
            If ``decimation`` is not an integer.
        ValueError
            If the decimation value is outside the supported range.
        """

        if type(decimation) != int:
            raise TypeError(f"Decimation type should be int.")

        if decimation not in [1, 2, 4, 8, 16] and not (17 <= decimation <= 65536):
            raise ValueError(
                f"Decimation of {decimation} is not allowed. "
                f"Should be one of [1, 2, 4, 8, 16] or any integer between 17 and 65536.")
        
        self.decimation = decimation

    def set_waveform_amplitude(self, amplitude: float) -> None:
        """        
        Set the normalized amplitude of the waveforms generated

        Parameters
        ----------
        amplitude : float
            Amplitude of the waveforms to control the FOV of the microscope

        Raises
        ------
        ValueError
            If the amplitude is outside of the possible range.
        """

        if not 0 <= amplitude <= 1:
            raise ValueError("Waveform amplitude should be between 0 and 1")

        self.amplitude = amplitude

    def set_image_size(self, image_size: int) -> None:
        """        
        Set the image size in pixels (128, 512 or 1024 are supported)

        Parameters
        ----------
        image_size : int
            Image size in pixels

        Raises
        ------
        ValueError
            If the image size is not supported.
        """

        if image_size not in [128, 512, 1024]:
            raise ValueError("Image size not in supported values (128, 512, 1024)")

        self.image_size = image_size

    def get_buffer_time_length_from_decimation(self) -> float:
        """
        Compute the time length (in seconds) of the Red Pitaya acquisition buffer
        for a given decimation factor.

        The Red Pitaya ADC runs at a base clock of 125 MHz. A decimation factor
        reduces the effective sampling rate according to:

            sampling_rate = 125e6 / decimation

        Since each acquisition buffer contains exactly 16 384 samples, the total
        buffer duration is:

            buffer_length = 16384 / sampling_rate

        Returns
        -------
        float
            Duration of the acquisition buffer in seconds.
        """

        clock_frequency = 125e6 # spec of the RedPitaya
        frequency = clock_frequency/self.decimation
        period = 1/frequency
        buffer_length = self.buffer_size * period

        return buffer_length

    def intialize(self) -> None:
        """
        Complete initialization of the microscope. Generator ports and acquisition port
        are reset and configured with the specified parameters.

        All in one function to configure the microscope easily

        The slow generation is not configured yet since the waveform generated will change 
        during acquition

        See self.acquire_image function to access the slow waveform set up
        """

        # set up generator parameters
        self.reset_generator()
        self.set_up_generator_ports()
        self.set_up_fast_waveform()
        self.enable_generator()

        # set up acquisition parameters
        self.reset_acquisition()
        self.set_up_acquisition()
        self.enable_acquisition()

    def reset_settings(self) -> None:
        """
        Complete reset of the acquisition and generator settings. Should be called after using
        the microscope to set the galvo mirrors back to zero position.
        """
        self.reset_generator()
        self.reset_acquisition()


    def set_up_acquisition(self) -> None:
        """
        Configure the acquisition module with default settings:
        - Enable averaging
        - Set decimation
        - Set trigger delay
        - RAW units
        - Debouncer time
        """
        self.acquisition.reset()
        self.acquisition.set_averaging_state('ON')
        self.acquisition.set_decimation(self.decimation)
        self.acquisition.set_trigger_delay(8192) # only get samples after the trigger
        self.acquisition.set_units('RAW')
        self.acquisition.set_debouncer_time(100)

    def arm_acquisition_trigger(self) -> None:
        """
        Arm the acquisition system by enabling external positive-edge trigger mode.
        """
        self.acquisition.set_trigger_mode('EXT_PE')

    def reset_generator(self) -> None:
        """
        Reset the function generator controller and both channels.
        """
        self.generator.reset()

    def enable_generator(self) -> None:
        """
        Enable generator output on all ports.
        """
        self.generator.enable()

    def disable_generator(self) -> None:
        """
        Disable generator output on all ports.
        """
        self.generator.disable()

    def set_up_generator_ports(self) -> None:
        """
        Configure both generator ports in burst mode with:
        - Fast channel: one burst containing `image_size` cycles
        - Slow channel: one burst containing one cycle
        - External positive-edge triggering
        - Shared debouncer time
        """
        self.fast_port.switch_to_burst_mode()
        self.fast_port.set_waveform_number_in_burst(self.buffer_size/self.image_size)
        self.fast_port.set_burst_number(1)
        self.fast_port.set_trigger_mode("EXT_PE")

        self.slow_port.switch_to_burst_mode()
        self.slow_port.set_waveform_number_in_burst(1)
        self.slow_port.set_burst_number(1)
        self.slow_port.set_trigger_mode("EXT_PE")

        self.generator.set_debouncer_time(100)

    def set_up_fast_waveform(self) -> None:
        """
        Create and upload arbitrary sawtooth waveforms to the fast and slow ports.
        Waveforms are normalized from -1 to +1 and scaled by the amplitude.
        """
        period_slow = self.get_buffer_time_length_from_decimation()

        period_fast = period_slow/(self.buffer_size/self.image_size) # width of a pulse in seconds
        freq_fast =  1/period_fast # related to the length of the pulse (1/frequency)

        # fast waveform
        points = self.buffer_size # number of total samples, must be this value
        signal_fast = np.linspace(-1, 1, points) # transition -1 -> 1
        data_str_fast = ','.join(f'{x:.5f}' for x in signal_fast) # convert to string

        self.fast_port.set_waveform(data_str_fast)          # must come before setting type
        self.fast_port.set_waveform_type("ARBITRARY")
        self.fast_port.set_fequency(freq_fast)
        self.fast_port.set_amplitude(self.amplitude)

        # slow waveform will be set during acquisition since it is changing for each block

    def enable_acquisition(self) -> None:
        """
        Start the acquisition engine and begin listening for triggers.
        """
        self.acquisition.start()

    def disable_acquisition(self) -> None:
        """
        Stop the acquisition engine.
        """
        self.acquisition.stop()
    
    def reset_acquisition(self) -> None:
        """
        Reset the acquisition engine
        """
        self.acquisition.reset()

    def trigger_acquisition(self) -> None:
        """
        Emit a trigger pulse on the digital pin (HIGH → LOW).
        Used to start waveform generation and data capture.
        """
        self.trigger_pin.set_high()
        self.trigger_pin.set_low()

    def acquire_image(self, show_progress: bool = True, normalize_image: bool = True) -> np.ndarray:
        """
        Acquire a complete 2D image using a 16384 buffer. Many buffers will be acquired if needed.

        Procedure for each buffer:
        1) Arm acquisition
        2) Start acquisition engine
        3) Send external trigger pulse
        4) Wait for trigger and buffer update
        5) Retrieve buffer

        The full image is then built using all buffers. The image is normalized from 0 to 255.

        Parameters
        -------
        show_progress : bool
            progress bar will be shown during acquisition if True

        normalize_image : bool
            image will be normalized in range 0-255 is True

        Returns
        -------
        np.ndarray
            2D image of shape (self.image_size, self.image_size)
        """

        period_slow = self.get_buffer_time_length_from_decimation()
        freq_slow =  1/period_slow # related to the length of the pulse (1/frequency)
        
        points_slow = self.image_size * self.image_size # number of data points for a full image
        n_buffers = points_slow//self.buffer_size  # number of buffers to acquire full image

        signal_slow = np.linspace(-1, 1, points_slow) # transition -1 -> 1
        signal_slow = signal_slow.reshape((n_buffers, self.buffer_size)) # matrix of slow signal for all 16 blocks
        # image to save blocks
        image_array = np.zeros(self.image_size*self.image_size)   


        # acquire all required blocks sequentially
        for i in tqdm(range(n_buffers), desc="Image acquisition", disable=(not show_progress)):

            # update slow waveform
            data_str_slow = ','.join(f'{x:.5f}' for x in signal_slow[i,:])
            self.slow_port.set_waveform(data_str_slow)          # must come before setting type
            self.slow_port.set_waveform_type("ARBITRARY")
            self.slow_port.set_fequency(freq_slow)
            self.slow_port.set_amplitude(self.amplitude)
            self.slow_port.set_default_last_voltage(signal_slow[i,-1])

            # Acquisition settings
            # needs to be done every time to arm the acquisition port after a trigger
            self.reset_acquisition()
            self.set_up_acquisition()
            self.arm_acquisition_trigger()
            self.enable_acquisition()
            
            # send trigger pulse
            self.trigger_acquisition()

            # wait for sweep
            self.acquisition.wait_for_trigger()
            self.acquisition.wait_for_buffer_update()
            
            # retreive data buffer
            buffer = self.acquisition.get_data_buffer(1)

            # save buffer in image
            image_array[i*self.buffer_size: (i+1)*self.buffer_size] = buffer

        # reshape image
        image = image_array.reshape((self.image_size, self.image_size))
        
        # flip image
        image = image[::-1,::-1]

        # normalize image
        if normalize_image:
            image_min = np.min(image)
            image_max = np.max(image)
            image = 255 * (image - image_min) / (image_max - image_min)

        return image

    def acquire_many_images(self, number_of_images: int,
                            show_progress: bool = True,
                            normalize_image: bool = True) -> np.ndarray:
        """
        Acquire multiple images sequentially.

        Parameters
        ----------
        number_of_images : int
            Number of frames to capture.

        show_progress : bool
            progress bar will be shown during acquisition if True

        normalize_image : bool
            image will be normalized in range 0-255 is True

        Returns
        -------
        np.ndarray
            3D stack of images with shape (N, image size, image size).
        """
        image_stack = np.zeros((number_of_images, self.image_size, self.image_size))

        for i in range(number_of_images):
            image = self.acquire_image(show_progress=show_progress, normalize_image=normalize_image)
            image_stack[i, ...] = image

        return image_stack

    def continuous_acquisition(self, n_images: int = 1000, 
                            show_progress: bool = True,
                            normalize_image: bool = True,
                            color_bar_max: int = 255,
                            color_bar_min: int = 0,
                            colormap: str = 'gray') -> None:
        """
        Live plotting of continuous image acquisiton. A matplotlib window will
        appear and display the images continuously. The acquisition frequency will
        be reduced since the figure needs to be updated.

        For faster acquisition, use aquire_many_images().

        Parameters
        ----------
        number_of_images : int
            Number of frames to capture and display before stopping automatically
            to avoid an infinite loop.

        show_progress : bool
            progress bar will be shown during acquisition if True

        normalize_image : bool
            image will be normalized in range 0-255 is True

        color_bar_max : int
            maximum value of the colorbar of the figure

        color_bar_min: int
            minimum value of the colorbar of the figure

        colormpap: str
            matplotlib colormap of the figure
        """
        def stop_acquisition(event):
            print("Stop button pressed.")
            stop_flag["stop"] = True

        # acquire first image to initialize figure
        image = self.acquire_image()

        # live plotting mode
        stop_flag = {"stop": False}   # mutable variable so callback can modify it
        plt.ion()                         # enable interactive mode
        fig = plt.figure()                # create one figure
        ax = fig.add_subplot(111)         # avoid plt.subplots()
        img_handle = ax.imshow(image, cmap=colormap, vmin=color_bar_min, vmax=color_bar_max)

        # attach colorbar explicitly to the figure
        fig.colorbar(img_handle, ax=ax)
        fig.canvas.draw()
        fig.canvas.flush_events()

        # add STOP button area
        stop_ax = fig.add_axes([0.81, 0.02, 0.16, 0.06])  # x, y, w, h
        stop_button = Button(stop_ax, "STOP", color='lightcoral', hovercolor='red')
        stop_button.on_clicked(stop_acquisition)

        try:
        # update figure with new image
            for i in range(n_images):

                # break loop if stop button is clicked
                if stop_flag["stop"]:
                    print("Stopping acquisition...")
                    break

                image = self.acquire_image(
                    show_progress=show_progress,
                    normalize_image=normalize_image
                )
                img_handle.set_data(image)

                # add STOP button area
                stop_ax = fig.add_axes([0.81, 0.02, 0.16, 0.06])  # x, y, w, h
                stop_button = Button(stop_ax, "STOP", color='lightcoral', hovercolor='red')
                stop_button.on_clicked(stop_acquisition)
    
                fig.canvas.draw_idle()
                fig.canvas.flush_events()

        except KeyboardInterrupt:
            print("\nKeyboard interrupt detected — stopping acquisition.")
            
        finally:
            # This always runs, even on exception
            plt.ioff()
            plt.close('all')
            print("Matplotlib window closed. Acquisition terminated.")
            self.reset_settings()
