from .acquisition_port import AcquisitionPort
from .scpi_controller import SCPIController
import numpy as np


class AcquisitionController:
    """
    Manages multiple acquisition ports on a Red Pitaya and provides
    control of the acquisition system through SCPI commands.

    This class allows configuration of acquisition parameters, including
    trigger mode, decimation, trigger delay, measurement units, and
    external trigger debouncer timing. It also provides functionality
    to start, stop, reset, and monitor the acquisition process, as well
    as retrieve data buffers from individual acquisition ports.

    The controller communicates with the Red Pitaya hardware using a
    SCPI controller instance and can manage multiple acquisition ports
    simultaneously.

    Attributes
    ----------
    ports : list of AcquisitionPort
        The list of acquisition port instances managed by this controller.
    scpi_controller : SCPIController
        An instance of a SCPI controller for communicating with the Red Pitaya.

    Notes
    -----
    - Trigger monitoring and buffer status can be polled to synchronize
        software operations with acquisition events.
    - Data buffers are returned as NumPy arrays for easy numerical processing.
    - All SCPI commands are sent via the provided SCPI controller instance,
        so proper initialization and connection to the Red Pitaya is required.
    - Port numbering is 1-based when retrieving data buffers.
    """

    def __init__(self, red_pitaya_scpi: SCPIController) -> None:
        """
        Initialize the acquisition controller.

        Parameters
        ----------
        red_pitaya_scpi : SCPIController
            The SCPI controller used to communicate with the Red Pitaya.
        """
        self.ports: list = []
        self.scpi_controller: SCPIController = red_pitaya_scpi

    def add_port(self, acquisition_port: AcquisitionPort) -> None:
        """
        Add an acquisition port to be managed by this controller.

        Parameters
        ----------
        acquisition_port : AcquisitionPort
            An instance of AcquisitionPort representing one input channel.
        """
        self.ports.append(acquisition_port)

    def set_trigger_mode(self, trigger_mode: str) -> None:
        """
        Configure the global acquisition trigger mode.

        Parameters
        ----------
        trigger_mode : str
            The trigger mode to set. Examples include 'EXT' for external trigger
            or 'IMMEDIATE' for immediate acquisition.

        Notes
        -----
        Sends the SCPI command `ACQ:TRIG <trigger_mode>` to the Red Pitaya.
        """
        self.scpi_controller.tx_txt(f'ACQ:TRIG {trigger_mode}')

    def start(self) -> None:
        """
        Start the acquisition process.

        Notes
        -----
        Sends the SCPI command `ACQ:START` to the Red Pitaya.
        """
        self.scpi_controller.tx_txt('ACQ:START')

    def stop(self) -> None:
        """
        Stop the acquisition process.

        Notes
        -----
        Sends the SCPI command `ACQ:STOP` to the Red Pitaya.
        """
        self.scpi_controller.tx_txt('ACQ:STOP')

    def reset(self) -> None:
        """
        Reset the acquisition system to default state.

        Notes
        -----
        Sends the SCPI command `ACQ:RST` to the Red Pitaya.
        """
        self.scpi_controller.tx_txt('ACQ:RST')

    def set_decimation(self, decimation: int) -> None:
        """
        Set the acquisition decimation factor.

        Parameters
        ----------
        decimation : int
            The decimation factor to apply. Higher values reduce the effective
            sample rate.

        Notes
        -----
        Sends the SCPI command `ACQ:DEC <decimation>` to the Red Pitaya.
        """
        self.scpi_controller.tx_txt(f'ACQ:DEC:Factor {decimation}')

    def set_trigger_delay(self, delay: int) -> None:
        """
        Set a delay for the acquisition trigger.

        Parameters
        ----------
        delay : int
            Trigger delay in sample units.

        Notes
        -----
        Sends the SCPI command `ACQ:TRIG:DLY <delay>` to the Red Pitaya.
        """
        self.scpi_controller.tx_txt(f'ACQ:TRIG:DLY {delay}')

    def set_units(self, units: str) -> None:
        """
        Set the measurement units for the data buffer.

        Parameters
        ----------
        units : str
            Units for the acquired data, e.g., 'V' for volts.

        Notes
        -----
        Sends the SCPI command `ACQ:DATA:Units <units>` to the Red Pitaya.
        """
        self.scpi_controller.tx_txt(f'ACQ:DATA:Units {units}')

    def set_debouncer_time(self, time: int) -> None:
        """
        Set the external trigger debouncer time.

        Parameters
        ----------
        time : int
            Debouncer time in microseconds.

        Notes
        -----
        Sends the SCPI command `ACQ:TRIG:EXT:DEBouncer:US <time>` to the Red Pitaya.
        """
        self.scpi_controller.tx_txt(f'ACQ:TRIG:EXT:DEBouncer:US {time}')

    def set_averaging_state(self, state: str) -> None:
        """
        Enable or disable acquisition averaging on the Red Pitaya.

        Parameters
        ----------
        state : str
            Averaging mode to apply. Typically `"ON"` to enable averaging
            or `"OFF"` to disable it. The value is passed directly to the
            SCPI command.

        Notes
        -----
        Sends the SCPI command `ACQ:AVG:<state>` to the Red Pitaya.
        Averaging reduces noise by averaging multiple acquisitions, but
        increases the effective acquisition time.
        """
        self.scpi_controller.tx_txt(f"ACQ:AVG:{state}")

    def wait_for_trigger(self) -> None:
        """
        Block until the acquisition system receives a trigger.

        Notes
        -----
        Polls the SCPI command `ACQ:TRIG:STAT?` until the status indicates
        the trigger has occurred. Prints status messages during polling.
        """
        while True:
            self.scpi_controller.tx_txt('ACQ:TRIG:STAT?')
            message = self.scpi_controller.rx_txt()
            if message == 'TD':
                break

    def wait_for_buffer_update(self) -> None:
        """
        Block until the acquisition buffer is full.

        Notes
        -----
        Polls the SCPI command `ACQ:TRIG:FILL?` until the buffer is filled.
        Prints buffer status messages during polling.
        """
        while True:
            self.scpi_controller.tx_txt('ACQ:TRIG:FILL?')
            message = self.scpi_controller.rx_txt()
            if message == '1':
                break

    def get_data_buffer(self, port_number: int) -> np.ndarray:
        """
        Retrieve the data buffer from a specified acquisition port.

        Parameters
        ----------
        port_number : int
            1-based index of the acquisition port to read.

        Returns
        -------
        np.ndarray
            The acquired data as a 1D NumPy array.

        Notes
        -----
        Calls the `get_data_buffer` method of the corresponding AcquisitionPort instance.
        """
        port = self.ports[port_number - 1]
        buffer = port.get_data_buffer()
        return buffer
