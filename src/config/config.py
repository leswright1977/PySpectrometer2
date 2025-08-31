from pydantic import BaseModel, Field
import cv2


# Application constants - user can't change them during runtime
class ApplicationConstants(BaseModel):
    camera_frame_width: int = Field(default=800, ge=100, le=1920)
    camera_frame_height: int = Field(default=600, ge=100, le=1080)
    frame_duration_limit: tuple[int, int] = Field(default=(33333, 33333))
    spectrograph_win_name: str = "PySpectrometer 2 - Spectrograph"
    waterfall_win_name: str = "PySpectrometer 2 - Waterfall"
    stack_height: int = 320 + 80 + 80
    gui_font: int = cv2.FONT_HERSHEY_SIMPLEX
    waterfall_array_height: int = 320
    cropped_image_height: int = 80  # We are interested in the middle 80px of the image
    calibration_data_file_path: str = "storage/calibration_data/caldata.txt"
    snapshot_folder: str = "storage/snapshots"
    testing_image_path: str = "not_testing"


# Runtime configuration - can be modified during execution
class RuntimeConfiguration(BaseModel):
    testing_mode: bool = Field(default=False)
    spectrometer_mode: str = Field(default="emittance_spectrometer")
    disp_full_screen: bool
    disp_waterfall: bool = False


# Initial values for state manager - will be changed during runtime
class StateManagerDefaults(BaseModel):
    default_picam_gain: float = Field(default=10.0, ge=0.0, le=50.0)
    default_savgol_filter_poly: int = Field(default=7, ge=0, le=15)
    default_savgol_filter_window_size: int = Field(default=17)
    default_minimum_distance_betw_peaks: int = Field(default=50, ge=0, le=100)
    default_threshold: int = Field(default=20, ge=0, le=100)


class UserConfiguration(BaseModel):
    constants: ApplicationConstants
    runtime_config: RuntimeConfiguration
    state_defaults: StateManagerDefaults