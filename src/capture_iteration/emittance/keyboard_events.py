from typing import Any
import numpy as np

from src.capture_iteration.emittance.save_snapshot import save_snapshot_of_current_spectrogram  # type: ignore
from src.calibration.write_calibration import write_calibration_data
from src.state_manager.state_manager import SpectrometerStateManager
from src.calibration.read_calibration import read_calibration_data
from src.gui.display_image import generate_graticule_for_gui


def listen_to_keyboard_events(
    cv2: Any,
    picam2: Any,
    spectrum_vertical: np.ndarray,
    state_manager: SpectrometerStateManager,
    camera_frame_width: int,
    calibration_data_file_path: str,
    snapshot_folder: str
):
    """
    Gomills: I really don't understand deeply what the keyboard events do, I just refactored it."""
    
    # Listen to keyboard events
    key_press = cv2.waitKey(1)
    if key_press == ord("q"): # tested
        return False

    elif key_press == ord("h"):
        state_manager.toggle_peak_hold()

    elif key_press == ord("s"): # tested
        # package up the data!
        save_data = {
            "px_to_wavelength_array": state_manager.get_calibration_data()["px_to_wavelength_array"],  # type: ignore
            "intensity_array": state_manager.get_intensity_array(),
            "spectrum_vertical": spectrum_vertical
        }

        message_to_set = (
            save_snapshot_of_current_spectrogram(save_data=save_data, cv2=cv2, snapshot_folder=snapshot_folder)
        )

        state_manager.set_save_status(message_to_set)

    elif key_press == ord("c"): # tested
        calibration_success = write_calibration_data(
            click_array_from_cv2=state_manager.get_click_array(),
            calibration_data_file_path=calibration_data_file_path)
        if calibration_success:
            # overwrite wavelength data
            # Go grab the computed calibration data
            px_to_wavelength_array, messages = read_calibration_data(
                camera_frame_width=camera_frame_width,
                calibration_data_file_path=calibration_data_file_path)
            new_graticule_data_dict = generate_graticule_for_gui(
                px_to_wavelength_array=px_to_wavelength_array,
            )
            state_manager.update_calibration_data(
                px_to_wavelength=px_to_wavelength_array, 
                messages=messages, 
                graticule_data=new_graticule_data_dict
            )
        else:
            state_manager.set_save_status("Calibration failed.")
            

    elif key_press == ord("x"): # tested
        state_manager.clear_calibration_clicks()
    elif key_press == ord("m"): # tested
        # This one just displays a cursor, it's too complicated the 
        # nomenclature around. It just displays a cursor with the wavelength instead
        # of the px with the calibration toggle p
        state_manager.toggle_measuring_mode()
    elif key_press == ord("p"): # tested
        state_manager.toggle_calibration_mode()
    elif key_press == ord("o"): # tested
        state_manager.adjust_savgol_filter(1)
    elif key_press == ord("l"): # tested
        state_manager.adjust_savgol_filter(-1)
    elif key_press == ord("i"): # tested
        state_manager.adjust_peak_distance(1)
    elif key_press == ord("k"): # tested
        state_manager.adjust_peak_distance(-1)
    elif key_press == ord("u"): # tested
        state_manager.adjust_threshold(1)
    elif key_press == ord("j"): # tested
        state_manager.adjust_threshold(-1)
    elif key_press == ord("v"):
        state_manager.adjust_camera_gain(1.0)
        picam2.set_controls({"AnalogueGain": state_manager.get_camera_gain()})
    elif key_press == ord("g"):
        state_manager.adjust_camera_gain(-1.0)
        picam2.set_controls({"AnalogueGain": state_manager.get_camera_gain()})
    elif key_press == ord("e"):
        state_manager.reset_before_mode_change()
        state_manager.change_spectrometer_mode("emittance_spectrometer")
    elif key_press == ord("t"):
        state_manager.reset_before_mode_change()
        state_manager.change_spectrometer_mode("transmittance_spectrometer")
    elif key_press == ord("w"):
        state_manager.reset_before_mode_change()
        state_manager.change_spectrometer_mode("waterfall_display")
    return True
