from .scpi_controller import SCPIController
import numpy as np

class AcquisitionPort:
    """
    Represents a single acquisition port on a Red Pitaya and allows
    reading the data buffer from that port.

    This class wraps the SCPI interface for a specific analog input channel
    and provides methods to retrieve the acquisition buffer as a NumPy array.

    The class is meant to simplify the SCPI commands sending to the Red Pitaya.
    Not all the possible commands are implemented.

    It is recommended to read the list of supported SCPI commands from the Red 
    Pitaya website to get all details.

    Parameters
    ----------
    port_number : int
        The Red Pitaya acquisition port number (e.g., 1 or 2).
    red_pitaya_scpi : scpi_controller
        An instance of a SCPI controller capable of sending commands to
        and receiving data from the Red Pitaya.
    """


    def __init__(self, port_number: int, red_pitaya_scpi: SCPIController) -> None:
        self.portNumber: int = port_number
        self.scpi_controller: SCPIController = red_pitaya_scpi


    def get_data_buffer(self) -> np.ndarray:
        """
        Retrieve the full acquisition buffer from the Red Pitaya for this port.

        Sends a SCPI command to request the data buffer, reads the
        response, converts the data to floating-point numbers, and
        returns it as a NumPy array.

        Returns
        -------
        np.ndarray
            A 1D NumPy array containing the sampled voltage data from
            the acquisition buffer.

        Notes
        -----
        - The SCPI command used is `ACQ:SOUR<port>:DATA?`.
        - The returned buffer is parsed from a string and converted to float.
        """

        # ask for full buffer
        self.scpi_controller.tx_txt(f'ACQ:SOUR{self.portNumber}:DATA?')

        # retrieve buffer
        buff_string = self.scpi_controller.rx_txt()

        # clean and split string to get values
        buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')

        # convert to float numpy array
        buffArray = np.array(list(map(float, buff_string)))

        return buffArray
