from .scpi_controller import SCPIController
import numpy as np


class GeneratorPort:
    """
    Represents a single signal generator output port on a Red Pitaya device
    and provides control over waveform generation settings.

    This class encapsulates all SCPI commands related to a specific
    generator channel, including waveform configuration, frequency and
    amplitude control, burst mode settings, and trigger configuration.

    Parameters
    ----------
    port_number : int
        The Red Pitaya generator port number (typically 1 or 2).
    red_pitaya_scpi : SCPIController
        The SCPI controller used to communicate with the Red Pitaya.

    Attributes
    ----------
    portNumber : int
        Identifier for the generator port managed by this instance.
    scpi_controller : SCPIController
        SCPI controller responsible for sending commands to the device.
    """

    def __init__(self, port_number: int, red_pitaya_scpi: SCPIController) -> None:
        """
        Initialize the generator port wrapper.

        Parameters
        ----------
        port_number : int
            Generator output channel number to control.
        red_pitaya_scpi : SCPIController
            SCPI controller instance used to send commands.
        """
        self.portNumber: int = port_number
        self.scpi_controller: SCPIController = red_pitaya_scpi

    def set_waveform(self, waveform: str) -> None:
        """
        Load custom waveform data into the generator buffer.

        Parameters
        ----------
        waveform : str
            A comma-separated list of numerical sample values formatted as
            required by the SCPI command. Typically produced by NumPy and
            converted to a string.

        Notes
        -----
        Sends the command `SOUR<n>:TRAC:DATA:DATA <waveform>`.
        """
        self.scpi_controller.tx_txt(f'SOUR{self.portNumber}:TRAC:DATA:DATA {waveform}')

    def set_waveform_type(self, waveform_type: str) -> None:
        """
        Set the generator waveform type.

        Parameters
        ----------
        waveform_type : str
            The waveform type to generate.

        Notes
        -----
        Sends the command `SOUR<n>:TRAC:FUNC <waveform_type>`.
        """
        self.scpi_controller.tx_txt(f'SOUR{self.portNumber}:FUNC {waveform_type}')

    def set_fequency(self, frequency: int) -> None:
        """
        Set the generator output frequency.

        Parameters
        ----------
        frequency : int
            Frequency in Hz to apply to the selected waveform.

        Notes
        -----
        Sends the command `SOUR<n>:FREQ:FIX <frequency>`.
        """
        self.scpi_controller.tx_txt(f'SOUR{self.portNumber}:FREQ:FIX {frequency}')
    
    def set_amplitude(self, amplitude: float) -> None:
        """
        Set the output amplitude of the generator channel.

        Parameters
        ----------
        amplitude : float
            Peak amplitude in volts (V).

        Notes
        -----
        Sends the command `SOUR<n>:VOLT <amplitude>`.
        """
        self.scpi_controller.tx_txt(f'SOUR{self.portNumber}:VOLT {amplitude}')
    
    def switch_to_burst_mode(self) -> None:
        """
        Enable burst mode on this generator port.

        Notes
        -----
        Sends the SCPI command `SOUR<n>:BURS:STAT BURST`, enabling burst mode
        but not configuring burst parameters.
        """
        self.scpi_controller.tx_txt(f'SOUR{self.portNumber}:BURS:STAT BURST')

    def set_waveform_number_in_burst(self, waveform_number: int) -> None:
        """
        Configure the number of waveform cycles per burst.

        Parameters
        ----------
        waveform_number : int
            Number of waveform periods contained in each burst.

        Notes
        -----
        Sends the command `SOUR<n>:BURS:NCYC <waveform_number>`.
        """
        self.scpi_controller.tx_txt(f'SOUR{self.portNumber}:BURS:NCYC {waveform_number}')

    def set_burst_number(self, burst_number: int) -> None:
        """
        Set the number of bursts to output.

        Parameters
        ----------
        burst_number : int
            Number of burst repetitions to generate.

        Notes
        -----
        Sends the command `SOUR<n>:BURS:NOR <burst_number>`.
        """
        self.scpi_controller.tx_txt(f'SOUR{self.portNumber}:BURS:NOR {burst_number}')
    
    def set_burst_period(self, burst_period: float) -> None:
        """
        Set the burst repetition period.

        Parameters
        ----------
        burst_period : float
            Period between bursts in seconds.

        Notes
        -----
        Sends the SCPI command `SOUR<n>:BURS:INT:PER <burst_period>`.
        """
        self.scpi_controller.tx_txt(f'SOUR{self.portNumber}:BURS:INT:PER {burst_period}')

    def set_trigger_mode(self, trigger_mode: str) -> None:
        """
        Configure the trigger source for burst mode or waveform initiation.

        Parameters
        ----------
        trigger_mode : str
            Trigger source string name.

        Notes
        -----
        Sends the SCPI command `SOUR<n>:TRIG:SOUR <trigger_mode>`.
        """
        self.scpi_controller.tx_txt(f'SOUR{self.portNumber}:TRIG:SOUR {trigger_mode}')
    
    def trigger_now(self) -> None:
        """
        Immediately triggers the waveform generator on this port.

        Sends a SCPI command to issue an internal trigger event for the
        selected output channel. This is typically used when the trigger
        source is set to internal (`INT`) and you want to force the
        generation of a waveform or burst without waiting for an external
        signal.

        Notes
        -----
        Sends the SCPI command ``SOUR<n>:TRIG:INT``.
        """
        self.scpi_controller.tx_txt(f"SOUR{self.portNumber}:TRIG:INT")

    def set_default_initial_voltage(self, voltage: float) -> None:
        """
        Set the initial output voltage level before waveform or burst generation.

        Parameters
        ----------
        voltage : float
            Initial voltage level in volts (V) that the generator will output
            before the waveform or burst sequence begins.

        Notes
        -----
        Sends the SCPI command `SOUR<n>:INITValue <voltage>`.
        """
        self.scpi_controller.tx_txt(f"SOUR{self.portNumber}:INITValue {voltage}")


    def set_default_last_voltage(self, voltage: float) -> None:
        """
        Set the final output voltage level after a burst sequence ends.

        Parameters
        ----------
        voltage : float
            Final voltage level in volts (V) that the generator will hold once
            the burst sequence has completed.

        Notes
        -----
        Sends the SCPI command `SOUR<n>:BURS:LASTValue <voltage>`.
        """
        self.scpi_controller.tx_txt(f"SOUR{self.portNumber}:BURS:LASTValue {voltage}")
    
    def enable(self) -> None: 
        """
        Enable the output state of the generator port. The port is now ready
        to produce an output when trigger condition is met.

        """
        self.scpi_controller.tx_txt(f"OUTPUT{self.portNumber}:STATE ON")

