# GUI Module

This module handles the graphical user interface for the spectrometer application using OpenCV.

## Files

- `display_image.py`: Contains functions for processing and rendering the display image, including:
  - Cropping captured images to the area of interest.
  - Drawing band lines, graticules, and colored spectrograms.
  - Displaying wavelength information at mouse positions.
  - Annotating spectral peaks with labels and flagpoles.

- `opencv_display.py`: Manages the OpenCV display window setup and mouse event handling:
  - Configures the window for full-screen or normal mode.
  - Tracks mouse movements and left-click events for calibration and measurement.

- `banner_image.png`: the banner image used in the GUI display (black brackground, contains project and authors's signatures)