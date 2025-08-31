# Config Parameters for PySpectrometer

This README explains the parameters in `config.json` that you can customize for the spectrometer application.

## Structure
The config is divided into three sections: `constants`, `runtime_config`, and `state_defaults`.

## Constants
These are fixed settings that define the application's behavior. They cannot be changed during runtime.

- **camera_frame_width**: Width of the camera frame in pixels (e.g., 800). Range: 100-1920.
- **camera_frame_height**: Height of the camera frame in pixels (e.g., 600). Range: 100-1080.
- **frame_duration_limit**: Tuple for frame duration limits in microseconds (e.g., [33333, 33333]). Controls camera timing.
- **testing_image_path**: Path to the image that substitutes camera's capture in testing mode (e.g., "src/config/spectrum_image_for_test.png"). Ignore this unless you're testing.

## Runtime Config
These settings can be modified during execution.

- **testing_mode**: Boolean (true/false). Enables testing mode, which skips camera initialization and uses a test image.
- **disp_full_screen**: Boolean (true/false). Whether to display the GUI in full screen.
- **disp_waterfall**: Boolean (true/false). Whether to display the waterfall view. KEEP false, waterfall view hasn't been developed yet

## State Defaults
Initial values for the spectrometer's state, adjustable during runtime.

- **default_picam_gain**: Float (e.g., 10.0). Initial camera gain. Range: 0.0-50.0.
- **default_savgol_filter_poly**: Integer (e.g., 7). Polynomial order for Savitzky-Golay filter. Range: 0-15.
- **default_savgol_filter_window_size**: Integer (e.g., 17). Window size for Savitzky-Golay filter.
- **default_minimum_distance_betw_peaks**: Integer (e.g., 50). Minimum distance between peaks in pixels. Range: 0-100.
- **default_threshold**: Integer (e.g., 20). Threshold for peak detection. Range: 0-100.

Edit `config.json` to change these values. Ensure they match the expected types and ranges to avoid errors.
