# Calibration Module

This module handles the calibration of the spectrometer: mapping pixel positions to wavelengths using polynomial fitting.

## Files

- `read_calibration.py`: Reads calibration data from a file and performs polynomial fitting to create a pixel-to-wavelength mapping.
  - Supports second-order (3 points) and third-order (>3 points) polynomial fits.
  - Calculates R-squared for fit quality assessment in third-order fits.
  - Returns a wavelength array for each pixel and calibration status messages.

- `write_calibration.py`: Writes new calibration data to a file based on user-provided pixel positions and wavelengths.
  - Prompts the user to input wavelengths for clicked pixel positions.
  - Saves the data in a comma-separated format to the calibration file.

## Usage

Calibration involves clicking on known spectral lines in the image and entering their wavelengths. The module then fits a polynomial to map pixels to wavelengths accurately.

## TODO
- Give the option to use higher of 3rd polynomial fitting. After all, the refactor of the old PySpectrometer2 now provides extra available overhead for these type of calculations
- As noted in storage/README.md, migrate the inadequate .txt file to a proper .csv with descriptive headers to improve professionalism and readability
