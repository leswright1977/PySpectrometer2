# PySpectrometer Source Code

This directory contains the source code.

## Main Entry Point

- `pyspectrometer_picam2.py`: The main script that orchestrates the application, loading configuration, setting up camera and GUI, and running the capture loop in different modes.

## Submodules

- `calibration/`: Handles spectrometer calibration mapping pixel positions to wavelengths using polynomial fitting.
- `config/`: Manages configuration parameters loaded from JSON files.
- `gui/`: Provides the graphical user interface using OpenCV, including image display and mouse interaction.
- `raspberry_camera/`: Sets up and configures the Raspberry Pi camera for video capture.
- `state_manager/`: Manages the application's state, including spectral data, operating modes, and processing parameters.
- `capture_iteration/`: Contains modules for different capture modes:
  - `emittance/`: Handles emittance spectroscopy capture and processing.
  - TODO:
    - `transmittance/`: Manages transmittance spectroscopy capture.
    - `waterfall/`: Implements waterfall display mode for spectral data visualization.

## Main used Dependencies

- OpenCV
- NumPy
- Picamera2 (for Raspberry Pi)
- Pydantic (for configuration validation)
