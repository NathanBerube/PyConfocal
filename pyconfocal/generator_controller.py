from .scpi_controller import SCPIController


class GeneratorController:
    """
    High-level controller for managing all Red Pitaya signal generator ports.

    This class is responsible for actions that apply globally to the
    generator subsystem, such as resetting the generator hardware,
    controlling output enable state, managing debouncing behavior for
    external triggers, and issuing simultaneous triggers to all ports.

    Parameters
    ----------
    red_pitaya_scpi : SCPIController
        The SCPI controller used to communicate with the Red Pitaya.
    """

    def __init__(self, red_pitaya_scpi: SCPIController) -> None:
        self.ports: list = []
        self.scpi_controller: SCPIController = red_pitaya_scpi

    def reset(self) -> None:
        """
        Reset the Red Pitaya generator subsystem.

        Sends the `GEN:RST` SCPI command, which clears generator
        configuration, resets internal counters, and prepares the system
        for new waveform and burst settings.
        """
        self.scpi_controller.tx_txt('GEN:RST')

    def trigger_all_ports(self) -> None:
        """
        Trigger all generator ports simultaneously.

        Issues the `SOUR:TRIG:INT` SCPI command, which performs a
        synchronous internal trigger across all fast analog outputs.
        The signal phase restarts from the beginning for all ports.
        """
        self.scpi_controller.tx_txt('SOUR:TRIG:INT')

    def enable(self) -> None:
        """
        Enable all generator outputs.

        Sends the SCPI command `OUTPUT:STATE ON`, turning on the physical
        analog output drivers for all configured generator ports.
        This must be enabled before any waveform can be observed on the
        Red Pitaya outputs.

        This function is equivalent to enabling both generator ports individually

        """
        self.scpi_controller.tx_txt('OUTPUT:STATE ON')

    def disable(self) -> None:
        """
        Disable all generator outputs.

        Sends the SCPI command `OUTPUT:STATE OFF`, which turns off the
        analog output drivers for all generator ports, regardless of
        their internal configuration or waveform state.
        """
        self.scpi_controller.tx_txt('OUTPUT:STATE OFF')

    def set_debouncer_time(self, time: int) -> None:
        """
        Configure the external trigger debouncer time.

        Parameters
        ----------
        time : int
            Debouncing duration in microseconds. This value defines how
            long the input must remain stable before being considered a
            valid external trigger.

        Notes
        -----
        This uses the command:
            `SOUR:TRIG:EXT:DEBOUNCER:US <time>`
        """
        self.scpi_controller.tx_txt(f'SOUR:TRig:EXT:DEBouncer:US {time}')
