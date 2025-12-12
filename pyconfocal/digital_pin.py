from .scpi_controller import SCPIController

class DigitalPin:

    """
    Control a digital I/O pin on a Red Pitaya using SCPI commands.

    This class provides a simple interface for configuring a digital pin as
    an output and driving it high or low. It directly wraps the SCPI commands
    used by the Red Pitaya API.

    Parameters
    ----------
    pin_name : str
        Identifier of the digital pin (e.g., "DIO0_P").
    red_pitaya : scpi
        A SCPI controller instance that can send commands to the Red Pitaya.
    """

    def __init__(self, pin_name: str, red_pitaya_scpi: SCPIController) -> None:
        self.pin_name: str = pin_name
        self.scpi_controller: SCPIController = red_pitaya_scpi


    def reset_all_pins(self) -> None:
        """
        Reset the digital subsystem of the Red Pitaya.

        Sends
        -----
        DIG:RST

        Notes
        -----
        This command resets *all* digital I/O pins, not only this one.
        """
        self.scpi_controller.tx_txt("DIG:RST")

    def set_direction(self, direction: str) -> None:
        """
        Configure the direction of the digital pin.

        Parameters
        ----------
        direction : str
            Pin direction "IN" or "OUT"

        Sends
        -----
        DIG:PIN:DIR OUT,<pin_name>
        """
        self.scpi_controller.tx_txt(f"DIG:PIN:DIR {direction},{self.pin_name}")


    def set_high(self) -> None:
        """
        Drive the pin to a logic HIGH level (3.3V).

        Sends
        -----
        DIG:PIN <pin_name>,1
        """
        self.scpi_controller.tx_txt(f"DIG:PIN {self.pin_name},1")


    def set_low(self) -> None:
        """
        Drive the pin to a logic LOW level (0V).

        Sends
        -----
        DIG:PIN <pin_name>,0
        """
        self.scpi_controller.tx_txt(f"DIG:PIN {self.pin_name},0")