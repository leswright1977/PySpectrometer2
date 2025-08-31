from typing import Any
from time import sleep

from src.capture_iteration.emittance.keyboard_events import listen_to_keyboard_events  # type: ignore
from src.capture_iteration.emittance.process_spectrum_intensities import (
    extract_spectral_intensities,
    filter_intensity_with_savitzky,
)
from src.state_manager.state_manager import SpectrometerStateManager
from src.calibration.read_calibration import read_calibration_data
from src.gui.display_image import generate_graticule_for_gui
from src.config.config import ApplicationConstants
from src.gui.display_image import (  # type: ignore
    show_px_at_mouse_position_for_calibration,
    show_wavelength_at_mouse_position,
    stack_images_and_display_spectrum,
    crop_capture_to_area_of_interest,
    draw_band_lines_on_display_image,
    draw_graticule_on_display_image,
    draw_colored_spectrogram,
    draw_clicks_as_circles,
)


# This function represents one iteration of the capture process: it's the process from taking the picture to processing it
def capture_emittance_iteration(
    picam2: Any, cv2: Any, static_elements: dict, constants: ApplicationConstants, state_manager: SpectrometerStateManager
) -> bool:
    # Deploy the static constants into usable objects for readability. These can't and won't be modified by the user
    GUI_FONT = constants.gui_font
    CAMERA_FRAME_WIDTH = constants.camera_frame_width
    CAMERA_FRAME_HEIGHT = constants.camera_frame_height
    SPECTROGRAPH_WIN_NAME = constants.spectrograph_win_name
    CROPPED_IMG_HEIGHT = constants.cropped_image_height
    static_elements["graph"].fill(255)  # Ensure the graph is white. This will erase previous mouse cross

    # (0/10) Check if we just changed the spectrometer 
    if state_manager.spectrometer_mode_just_changed():
        # Load calibration data through state manager (if it's start up, it will be the default)
        px_to_wavelength_array, calibration_messages = read_calibration_data(
            camera_frame_width=constants.camera_frame_width, calibration_data_file_path=constants.calibration_data_file_path
        )

        graticule_data_dict = generate_graticule_for_gui(px_to_wavelength_array)
        state_manager.update_calibration_data(px_to_wavelength_array, calibration_messages, graticule_data_dict)
    state_manager.increment_capture_iteration()

    # (1/10) Capture a live image, and allow for testing mode
    if not state_manager.is_testing_mode():
        raw_captured_image = picam2.capture_array()
    else:
        # In testing mode, we use a static image for testing purposes
        raw_captured_image = cv2.imread(constants.testing_image_path)
        sleep(0.5)

    # (2/10) Crop the image to the area of interest. This image has color, and is the one that will be displayed visually
    cropped_image = crop_capture_to_area_of_interest(
        camera_frame_height=CAMERA_FRAME_HEIGHT,
        camera_frame_width=CAMERA_FRAME_WIDTH,
        raw_captured_image=raw_captured_image,
        cropped_image_height=CROPPED_IMG_HEIGHT,
    )

    # (3/10) Convert the coloured cropped_image image to a grayscale image which will be used for data extraction
    bw_cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    number_of_pixel_rows, number_of_pixel_columns = bw_cropped_image.shape
    halfway_height_px = number_of_pixel_rows // 2

    # (4/10) Draw visual guide lines on the display image to show the 3px analysis band
    draw_band_lines_on_display_image(
        cv2=cv2, cropped_image=cropped_image, halfway_height_px=halfway_height_px, camera_frame_width=CAMERA_FRAME_WIDTH
    )

    # (5/10) Display a graticule aligned with calibration data
    draw_graticule_on_display_image(
        cv2=cv2,
        text_offset=12,
        gui_font=GUI_FONT,
        static_elements=static_elements,
        camera_frame_width=CAMERA_FRAME_WIDTH,
        graticule_data_dict=state_manager.get_graticule_data(),
    )

    # (5/10) Extract the spectral intensities from the grayscale image
    extract_spectral_intensities(
        bw_cropped_image=bw_cropped_image,
        halfway_height_px=halfway_height_px,
        number_of_pixel_columns=number_of_pixel_columns,
        state_manager=state_manager,
    )

    # (6/10) Filter the intensity data and update it (only filters if not in peak-hold mode)
    filter_intensity_with_savitzky(state_manager=state_manager)

    # (7/10) Draw the colored spectrogram with the intensity array for the GUI
    draw_colored_spectrogram(
        cv2=cv2,
        state_manager=state_manager,
        static_elements=static_elements,
        gui_font=GUI_FONT,
    )

    # (8/10) This section handles mouse interactions in the GUI
    # When a keyboard binding is clicked, it will display a cursor with the wavelength at the mouse position.
    show_wavelength_at_mouse_position(cv2=cv2, gui_font=GUI_FONT, state_manager=state_manager, static_elements=static_elements)

    # When the user is calibrating, it will display a cursor with the pixel at the mouse position.
    show_px_at_mouse_position_for_calibration(
        cv2=cv2, gui_font=GUI_FONT, state_manager=state_manager, static_elements=static_elements
    )

    # Draw each click as a circle on the spectrogram when calibrating
    draw_clicks_as_circles(
        cv2=cv2,
        static_elements=static_elements,
        state_manager=state_manager,
    )

    # (9/10) Stack the images and display the spectrum on the GUI finally
    spectrum_vertical = stack_images_and_display_spectrum(
        cv2=cv2,
        static_elements=static_elements,
        cropped_image=cropped_image,
        state_manager=state_manager,
        gui_font=GUI_FONT,
        camera_frame_width=CAMERA_FRAME_WIDTH,
        spectrograph_win_name=SPECTROGRAPH_WIN_NAME,
    )

    # (10/10) Listen to keyboard events for user interactions. This allows direct interaction with the state of
    # the spectrometer, such as toggling peak hold, measuring mode, and calibration mode.
    return listen_to_keyboard_events(
        cv2=cv2,
        picam2=picam2,
        spectrum_vertical=spectrum_vertical,
        state_manager=state_manager,
        camera_frame_width=CAMERA_FRAME_WIDTH,
        snapshot_folder=constants.snapshot_folder,
        calibration_data_file_path=constants.calibration_data_file_path
    )
