from typing import Any
import numpy as np

from src.capture_iteration.emittance.spectroscopy_calculations import savitzky_golay # type: ignore
from src.state_manager.state_manager import SpectrometerStateManager

def extract_spectral_intensities(
        bw_cropped_image: Any,
        halfway_height_px: int,
        number_of_pixel_columns: int,
        state_manager: SpectrometerStateManager,
):
    """
    Extracts spectral intensity data by averaging a 3-pixel vertical band across each column.
    
    For each column, averages the pixel values at halfway_height_px-1, halfway_height_px, 
    and halfway_height_px+1 to generate the spectral intensity for that wavelength position.
    """

    # Get the [average array] from the 3 rows
    rows = bw_cropped_image[halfway_height_px - 1 : halfway_height_px + 1 + 1, :] # stop index is exclusive in python, that's why +1 + 1
    averaged_intensity_uint8 = np.mean(rows.astype(np.int32), axis=0).astype(np.uint8)

    for pxcol in range(number_of_pixel_columns):

        # By validating we mean to update intensity only if we are in peak-hold mode. Otherwise, it auto-returns the value
        validated_intensity = state_manager.validate_intensity_extraction(
            peak_hold_mode=state_manager.is_peak_hold_active(),
            current_intensity=averaged_intensity_uint8[pxcol], 
            pixel_index=pxcol
        )
        state_manager.set_intensity_at_index(index=pxcol, intensity=validated_intensity)

def filter_intensity_with_savitzky(
        state_manager: SpectrometerStateManager
):
    """
    Applies Savitzky-Golay smoothing filter to intensity data when not in peak-hold mode
    and updates the intensity array in the spectrometer state variables.
    
    Returns status string indicating whether peak-hold mode is active.
    """

    SAVGOL_FILTER_WINDOW_SIZE = state_manager.get_savgol_filter_window_size()
    
    # Apply smoothing filter if not in peak-hold mode
    if state_manager.should_apply_smoothing_filter():
        # Get the raw smoothed intensity array
        raw_smoothed_intensity = savitzky_golay(
            state_manager.get_intensity_array(), 
            SAVGOL_FILTER_WINDOW_SIZE, 
            state_manager.get_savgol_filter_poly()
        )
        
        # Convert to integers and update state
        smoothed_intensity_array = np.array(raw_smoothed_intensity).astype(int)
        state_manager.update_intensity_array(smoothed_intensity_array)
