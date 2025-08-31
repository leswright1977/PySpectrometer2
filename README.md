# PySpectrometer2 Refactor

A Python-based spectrometer application designed for use with Raspberry Pi. This application captures images from the Raspberry Pi camera, processes them into spectral data, and provides a GUI for visualization and calibration.

I (Gomills) made this codebase as a refactor of the amazing repo https://github.com/leswright1977/PySpectrometer2, by Les Wright, the original author. 
My aim was to convert a script-type software to a more defined and modern codebase by:

- Modernizing to 2025's Python Standards
- Modularizing
- Documenting
- Improving readability and clarity
- Memory safety
- Not so much focus (though big things happened): optimization

This resulted, or at least I hope, into an environment that invites developers and any user to contribute/modify the software for everyone's purpose and to maintain the repo by modernizing it to today's software standards.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

This is a derivative work based on the original PySpectrometer2 by Les Wright.

## User Guide

### Installation

0. **Download this repo**: as a zip and extract it in your Raspberry Pi. Place it in a comfortable, or any that you choose, folder.  

Follow these steps to install the required dependencies on your Raspberry Pi. If you don't understand or find it difficult, copy and paste this README.md and ask ChatGPT.

1. **Check and Install picamera2:**

   ```bash
   if python3 -c "import picamera2" &> /dev/null; then
       version=$(python3 -c "import picamera2; print(getattr(picamera2, '__version__', 'unknown'))")
       path=$(python3 -c "import picamera2; print(picamera2.__file__)")
       echo "picamera2 is installed"
       echo "Version: $version"
   else
       echo "picamera2 is not installed. Proceeding to install..."
       sudo apt install python3-picamera2
   fi
   ```

2. **Check and Install numpy:**

   ```bash
   if python3 -c "import numpy" &> /dev/null; then
       version=$(python3 -c "import numpy; print(numpy.__version__)")
       path=$(python3 -c "import numpy; print(numpy.__file__)")
       echo "numpy is installed"
       echo "Version: $version"
   else
       echo "numpy is not installed. Proceeding to install..."
       sudo python3 -m pip install "numpy>=2.2.6"
   fi
   ```

3. **Install pydantic and opencv-python:**

   ```bash
   sudo python3 -m pip install "pydantic>=2.11.7"; sudo python3 -m pip install "opencv-python>=4.12.0.88"
   ```

   To verify opencv installation:

   ```bash
   if python3 -c "import cv2" &> /dev/null; then
       version=$(python3 -c "import cv2; print(cv2.__version__)")
       path=$(python3 -c "import cv2; print(cv2.__file__)")
       echo "opencv-python is installed"
       echo "Version: $version"
       echo "Path: $path"
   else
       echo "opencv-python is not installed"
   fi
   ```

### Usage

Once all dependencies are installed and your Raspberry Pi camera is properly set up (refer to Les Wright's videos for hardware setup guidance), you can run the spectrometer application.

#### Running the Application

Navigate to the project directory (use the 'cd' command and the help of ChatGPT) and execute:

```bash
python3 main.py
```

This will start the spectrometer in its default mode. The application will:

1. Load configuration from `src/config/config.json`
2. Initialize the Raspberry Pi camera using picamera2
3. Launch the OpenCV-based GUI for real-time display
4. Begin capturing and processing spectral data

#### User Interface

- **Display**: Real-time camera feed with overlaid spectral information
- **Mouse Interaction**: Click on spectral lines for calibration and measurement
- **Key Bindings**: Use keyboard shortcuts to switch modes and perform actions (refer to in-app help or source code for details). Refer to Les Wright videos where he explains how to set it up

#### Configuration

Customize behavior by editing `src/config/config.json`:

- Camera settings (resolution, frame rate)
- Processing parameters (filter settings, peak detection)
- GUI options (full screen, display modes)

#### Tips

- For detailed setup instructions, watch Les Wright's original PySpectrometer2 videos

## Developer Guide

### Software Architecture and Algorithm

- **Image Capture and Processing**: Captures frames from Raspberry Pi camera, crops to central band, converts to grayscale, and averages intensities for noise reduction.
- **Pixel-to-Wavelength Conversion**: Uses polynomial fitting (2nd or 3rd order) based on calibration points to map pixel positions to wavelengths.
- **Modes**:
  - Emittance: Handles emittance spectroscopy capture and processing.
  - Transmittance: Manages transmittance spectroscopy capture (TODO).
  - Waterfall: Implements waterfall display for spectral data visualization (TODO).
- **GUI**: OpenCV-based interface for display and user interaction.
- **State Management**: Each user session is described by a state manager, an encapsulated class object that contains all runtime variables and methods to modify them ("Single Source of Truth")
- **Configuration**: JSON-based configuration for constants, runtime settings, and defaults.

### Dependencies

This project requires several Python packages and OS-level dependencies, particularly for Raspberry Pi camera support. Note that due to OS-level interactions, virtual environments cannot be used. Picamera2 for Python is preinstalled on Raspberry Pi OS Bullseye (or later) images, as well as Numpy. However installation for those is provided in any case in this README.md.

#### Python Packages

- **opencv-python**: Handles image capture, processing, display, and GUI operations.
- **numpy**: Provides numerical computations, array manipulation, and polynomial fitting for wavelength calibration.
- **picamera2**: Interfaces with the Raspberry Pi camera, built on top of libcamera2 for hardware access. Their developers insist in using apt to ensure installing alongside a compatible libcamera library, which is OS-level
- **pydantic**: Validates and manages configuration data from JSON files.

```

While picamera2 can be installed using pip (`pip install picamera2`), this may result in version mismatches between picamera2 and libcamera, potentially causing issues. Their developers recommend using apt.
```
#### Important Notes

- The interaction between picamera2 and the OS-level libcamera2 library makes it impossible to use virtual environments. All dependencies must be installed system-level.
- This limitation prevents the use of comfortable Python package managers like uv
- But this shouldn't bee too much of a hassle since it's run on a Raspberry pi and not a personal computer used for multipurposes

### TODOs

- Update GUI to include more info
- Refactor key bindings
- Add option for higher-order polynomial fitting in calibration.
- Migrate calibration data from .txt to .csv with descriptive headers.
- Add more descriptive logging
- Introduce more testing.
- Implement transmittance and waterfall mode (this should happen after all other TODOs are accomplished. Because if done otherwise, it will be a real mess)

### Licensing

This project is a derivative work of PySpectrometer2 by Les Wright, licensed under Apache License 2.0. When contributing:

- Ensure all new files include the Apache License header
- Preserve original copyright notices
- Document any significant modifications
- Follow Apache License 2.0 terms for redistribution