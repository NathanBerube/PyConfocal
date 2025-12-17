# PyConfocal package
For a complete control of a sweeping confocal microscope with a Red Pitaya using Python.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Notes](#notes)

## Installation
It is possible to download the package directly from the GitHub repository on your computer using:
```bash
pip install git+https://github.com/NathanBerube/PyConfocal.git
```

## Usage

The package offers 7 classes for the control of the Red Pitaya. Six of them are for direct control of the Red Pitaya and are completely independent fom the microscope itself. they could be use The other one, the See [`ConfocalMicroscope`](confocal_microscope.py) class, is an all-in-one class to acquire images with the microscope and specify desired acquisition parameters. Here is a summary of all classes purposes.

- [`AcquisitionController`](acquisition_controller.py): Manages multiple acquisition ports on a Red Pitaya and provides
    control of the acquisition system through SCPI commands. This class allows configuration of acquisition parameters, including
    trigger mode, decimation, trigger delay, measurement units, and
    external trigger debouncer timing. It also provides functionality
    to start, stop, reset, and monitor the acquisition process, as well
    as retrieve data buffers from individual acquisition ports.

- [`AcquisitionPort`](acquisition_port.py): Represents a single acquisition port on a Red Pitaya and allows
    reading the data buffer from that physical port on the Red Pitaya.This class wraps the SCPI interface for a specific analog input channel
    and provides methods to retrieve the acquisition buffer as a NumPy array.
  
- [`DigitalPin`](digital_pin.py): Control a digital I/O pin on a Red Pitaya using SCPI commands. This class provides a simple interface for configuring a digital pin as
    an output and driving it high or low. It directly wraps the SCPI commands
    used by the Red Pitaya API.
  
- [`GeneratorController`](generator_controller.py): Controller for managing all Red Pitaya signal generator ports.This class is responsible for actions that apply globally to the
    generator subsystem, such as resetting the generator hardware,
    controlling output enable state, managing debouncing behavior for
    external triggers, and issuing simultaneous triggers to all ports.
  
- [`GeneratorPort`](generator_port.py): Represents a single signal generator output port on a Red Pitaya device
    and provides control over waveform generation settings. This class encapsulates all SCPI commands related to a specific
    generator channel, including waveform configuration, frequency and
    amplitude control, burst mode settings, and trigger configuration.

- [`SCPIController`](scpi_controller.py): SCPI class used to access Red Pitaya over an IP network. It is from the Red Pitaya repository. (Luka Golinar and Iztok Jera, 2015).

- [`ConfocalMicroscope`](confocal_microscope.py): Controller for a confocal scanning microscope based on a Red Pitaya device. This class controls the generator configuration (fast and slow scanning axes) for the sweeping of the field of view, the acquisition setup and synchronization, the trigger handling through a digital pin, a rampe waveform generation for galvo scanning and automated image acquisition (single or multiple). The class ensures proper synchronization between waveform generation and acquisition to perform frame scans.


The details of each class can be found in the .py files. For more details on the SCPI commands sent, the [list of SCPI commands](https://redpitaya.readthedocs.io/en/latest/appsFeatures/remoteControl/command_list.html) should be consulted.

  
Some general information on the SCPI server hosted by the Red Pitaya can be found on this [web page](https://redpitaya.readthedocs.io/en/latest/appsFeatures/remoteControl/scpi.html).

## Examples
The [examples](examples/) folder contains a few simple example scripts for image acquisition using the package. The IP address of the Red Pitaya needs to be specified in the code before being able to run the script (and the saving path if needed). An example script can be run using:
```bash
cd PyConfocal
python -m examples.acquire_single_image
```
from the **root of the repository**. Change the example file name to the approriate one.

# Notes
- The code was only tested on a StemLab 125-14 Red Pitaya. Using the package on another version might not result in expected outcomes.


Nathan Bérubé, December 2025
  
