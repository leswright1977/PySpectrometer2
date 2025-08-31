from typing import Any
import numpy as np

from src.config.config import StateManagerDefaults


class SpectrometerStateManager:
    def __init__(self, camera_width: int, default_calculus_params: StateManagerDefaults, testing_mode: bool, running_mode: str = "emittance_spectrometer") -> None:
        # Spectral Data State
        self.intensity_array: np.ndarray = np.zeros(camera_width, dtype=np.uint8)
        self.waterfall_array: np.ndarray = np.zeros([320, camera_width, 3], dtype=np.uint8)
        self.px_to_wavelength_array: np.ndarray = np.zeros(camera_width, dtype=np.float64)
        self.calibration_messages: dict[str, Any] = {}
        self.graticule_data_dict: dict = {}

        # Operating Mode State
        self.are_we_holding_peaks: bool = False
        self.are_we_measuring: bool = False
        self.are_we_calibrating: bool = False

        # Mouse/GUI Interaction State
        self.cursor_x: int = 0
        self.cursor_y: int = 0
        self.click_array: list = []
        self.last_save_message_status: str = "No data saved"

        # Processing Parameters State
        self.threshold: int = default_calculus_params.default_threshold
        self.savgol_filter_poly: int = default_calculus_params.default_savgol_filter_poly
        self.savgol_filter_window_size: int = default_calculus_params.default_savgol_filter_window_size
        self.minimum_distance_betw_peaks: int = default_calculus_params.default_minimum_distance_betw_peaks

        # Camera Control State
        self.picam_gain: float = 10.0

        # Spectrometer Mode
        self.spectrometer_mode: str = running_mode
        self.testing_mode: bool = testing_mode
        self.spectrometer_capture_iteration: int = 0

    # State Access Methods
    def get_intensity_array(self) -> np.ndarray:
        return self.intensity_array

    def get_calibration_data(self) -> dict:
        return {"px_to_wavelength_array": self.px_to_wavelength_array, "calibration_messages": self.calibration_messages}

    def get_graticule_data(self) -> dict:
        return self.graticule_data_dict

    def get_mouse_position(self) -> tuple[int, int]:
        return (self.cursor_x, self.cursor_y)

    def get_click_array(self) -> list:
        return self.click_array
    
    def get_spectrometer_mode(self) -> str:
        return self.spectrometer_mode
    
    def change_spectrometer_mode(self, new_mode: str) -> None:
        self.spectrometer_mode = new_mode
        return
    
    def is_testing_mode(self) -> bool:
        return self.testing_mode

    def is_peak_hold_active(self) -> bool:
        return self.are_we_holding_peaks

    def is_measuring_mode_active(self) -> bool:
        return self.are_we_measuring

    def is_calibration_mode_active(self) -> bool:
        return self.are_we_calibrating

    # State Modification Methods
    def toggle_peak_hold(self) -> bool:
        self.are_we_holding_peaks = not self.are_we_holding_peaks
        return self.are_we_holding_peaks

    def toggle_measuring_mode(self) -> None:
        self.are_we_calibrating = False
        self.are_we_measuring = not self.are_we_measuring

    def toggle_calibration_mode(self) -> None:
        self.are_we_measuring = False
        self.are_we_calibrating = not self.are_we_calibrating

    def update_intensity_array(self, new_data: np.ndarray) -> None:
        self.intensity_array = new_data

    def set_intensity_at_index(self, index: int, intensity: np.unsignedinteger) -> None:
        self.intensity_array[index] = intensity

    def update_mouse_position(self, x: int, y: int) -> None:
        self.cursor_x = x
        self.cursor_y = y

    def add_calibration_click(self, x: int, y: int) -> None:
        self.click_array.append([x, y])

    def clear_calibration_clicks(self) -> None:
        self.click_array.clear()

    def update_calibration_data(self, px_to_wavelength: np.ndarray, messages: dict, graticule_data: dict = {}) -> None:
        self.px_to_wavelength_array = px_to_wavelength
        self.calibration_messages = messages
        if graticule_data:
            self.graticule_data_dict = graticule_data

    def set_save_status(self, message: str) -> None:
        self.last_save_message_status = message

    # Parameter Adjustment Methods
    def adjust_savgol_filter(self, increment: int) -> int:
        self.savgol_filter_poly = max(0, min(15, self.savgol_filter_poly + increment))
        return self.savgol_filter_poly

    def adjust_peak_distance(self, increment: int) -> int:
        self.minimum_distance_betw_peaks = max(0, min(100, self.minimum_distance_betw_peaks + increment))
        return self.minimum_distance_betw_peaks

    def adjust_threshold(self, increment: int) -> int:
        self.threshold = max(0, min(100, self.threshold + increment))
        return self.threshold

    def adjust_camera_gain(self, increment: float) -> float:
        self.picam_gain = max(0.0, min(50.0, self.picam_gain + increment))
        return self.picam_gain
    
    def increment_capture_iteration(self) -> None:
        self.spectrometer_capture_iteration += 1

    def spectrometer_mode_just_changed(self) -> bool:
        return self.spectrometer_capture_iteration == 0

    # State Validation Methods
    def validate_intensity_extraction(
        self, peak_hold_mode: bool, current_intensity: np.unsignedinteger, pixel_index: int
    ) -> np.unsignedinteger:
        if peak_hold_mode:
            if current_intensity > self.intensity_array[pixel_index]:
                return current_intensity
            return self.intensity_array[pixel_index]
        return current_intensity

    def should_apply_smoothing_filter(self) -> bool:
        return not self.are_we_holding_peaks

    def get_peak_hold_status_message(self) -> str:
        return "Holdpeaks ON" if self.are_we_holding_peaks else "Holdpeaks OFF"

    def get_savgol_filter_poly(self) -> int:
        return self.savgol_filter_poly

    def get_threshold(self) -> int:
        return self.threshold

    def get_minimum_distance_betw_peaks(self) -> int:
        return self.minimum_distance_betw_peaks

    def get_save_status_message(self) -> str:
        return self.last_save_message_status

    def get_camera_gain(self) -> float:
        return self.picam_gain

    def get_savgol_filter_window_size(self) -> int:
        return self.savgol_filter_window_size

    # Initialization Methods
    def initialize_arrays(self, camera_width: int) -> None:
        self.intensity_array = np.zeros(camera_width, dtype=np.uint8)
        self.waterfall_array = np.zeros([320, camera_width, 3], dtype=np.uint8)
        self.px_to_wavelength_array = np.zeros(camera_width, dtype=np.float64)

    def set_to_defaults(self) -> None:
        self.are_we_holding_peaks = False
        self.are_we_measuring = False
        self.are_we_calibrating = False
        self.click_array.clear()
        self.last_save_message_status = "No data saved"
        self.savgol_filter_poly = 7
        self.minimum_distance_betw_peaks = 50
        self.threshold = 20
        self.picam_gain = 10.0

    def reset_before_mode_change(self) -> None:
        self.are_we_holding_peaks = False
        self.are_we_measuring = False
        self.are_we_calibrating = False
        self.click_array.clear()
        self.last_save_message_status = "No data saved"
        self.intensity_array.fill(0)
        self.waterfall_array.fill(0)
        self.spectrometer_capture_iteration = 0
