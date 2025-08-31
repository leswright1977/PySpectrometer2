
# SpectrometerStateManager Class Description

## Core Responsibility
Centralized management of all spectrometer state variables, providing controlled access and ensuring state consistency across the application.

## State Variables to Store

### 1. Spectral Data State
- `intensity_array: np.ndarray` - Current spectral intensity data (800 pixels wide)
- `waterfall_array: np.ndarray` - Waterfall display data for time-series visualization
- `px_to_wavelength_array: np.ndarray` - Pixel-to-wavelength calibration mapping
- `calibration_messages: dict` - Status messages about calibration quality and type
- `graticule_data_dict: dict` - Data for GUI graticule display

### 2. Operating Mode State
- `are_we_holding_peaks: bool` - Peak hold mode toggle
- `are_we_measuring: bool` - Wavelength measurement mode (crosshair cursor)
- `are_we_calibrating: bool` - Calibration mode (pixel recording)
- `spectrometer_mode: str` - Current spectrometer mode (e.g., "emittance_spectrometer")
- `testing_mode: bool` - Whether in testing mode
- `spectrometer_capture_iteration: int` - Iteration counter for capture loops

### 3. Mouse/GUI Interaction State
- `cursor_x, cursor_y: int` - Current mouse position
- `click_array: list` - Recorded calibration click positions
- `last_save_message_status: str` - Status of last data save operation

### 4. Processing Parameters State
- `savgol_filter_poly: int` - Savitzky-Golay filter polynomial order (0-15)
- `savgol_filter_window_size: int` - Filter window size (fixed at 17)
- `minimum_distance_betw_peaks: int` - Peak detection minimum distance (0-100)
- `threshold: int` - Peak labeling threshold (0-100)

### 5. Camera Control State
- `picam_gain: float` - Camera analog gain (0.0-50.0)

## Methods Implemented

### State Access Methods
```python
get_intensity_array() → np.ndarray
get_calibration_data() → dict
get_graticule_data() → dict
get_mouse_position() → tuple[int, int]
get_click_array() → list
get_spectrometer_mode() → str
is_testing_mode() → bool
is_peak_hold_active() → bool
is_measuring_mode_active() → bool
is_calibration_mode_active() → bool
get_savgol_filter_poly() → int
get_threshold() → int
get_minimum_distance_betw_peaks() → int
get_save_status_message() → str
get_camera_gain() → float
get_savgol_filter_window_size() → int
```

### State Modification Methods
```python
toggle_peak_hold() → bool
toggle_measuring_mode() → None  # auto-disables calibration mode
toggle_calibration_mode() → None  # auto-disables measuring mode
change_spectrometer_mode(new_mode: str) → None
update_intensity_array(new_data: np.ndarray) → None
set_intensity_at_index(index: int, intensity: np.unsignedinteger) → None
update_mouse_position(x: int, y: int) → None
add_calibration_click(x: int, y: int) → None
clear_calibration_clicks() → None
update_calibration_data(px_to_wavelength: np.ndarray, messages: dict, graticule_data: dict = {}) → None
set_save_status(message: str) → None
increment_capture_iteration() → None
```

### Parameter Adjustment Methods
```python
adjust_savgol_filter(increment: int) → int  # with bounds checking 0-15
adjust_peak_distance(increment: int) → int  # with bounds checking 0-100
adjust_threshold(increment: int) → int  # with bounds checking 0-100
adjust_camera_gain(increment: float) → float  # with bounds checking 0.0-50.0
```

### State Validation Methods
```python
validate_intensity_extraction(peak_hold_mode: bool, current_intensity: np.unsignedinteger, pixel_index: int) → np.unsignedinteger
should_apply_smoothing_filter() → bool
get_peak_hold_status_message() → str
spectrometer_mode_just_changed() → bool
```

### Initialization Methods
```python
initialize_arrays(camera_width: int) → None
set_to_defaults() → None
reset_before_mode_change() → None
```

## Key Design Principles

- **Encapsulation**: All state changes go through controlled methods, no direct property access
- **Validation**: Parameter adjustments include automatic bounds checking
- **Mode Management**: Measuring and calibration modes are mutually exclusive
- **State Consistency**: Related state changes are handled atomically
- **Initialization**: Clear separation between configuration loading and state initialization

## Integration Points

- Replaces direct access to `spectrometer_full_config` nested properties
- Provides clean interface for keyboard event handlers
- Centralizes all state-dependent logic from GUI display functions
- Manages the complex interaction between peak hold mode and intensity processing

## Summary

This design eliminates the old mess of scattered variable declarations and provides a single source of truth for all spectrometer state, making the code much more maintainable and debuggable.