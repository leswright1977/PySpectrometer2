from typing import Any
import numpy as np

from src.capture_iteration.emittance.spectroscopy_calculations import (  # type: ignore
    wavelength_to_rgb,
    find_peaks_in_array,
)
from src.state_manager.state_manager import SpectrometerStateManager


def crop_capture_to_area_of_interest(
    camera_frame_height: int, camera_frame_width: int, raw_captured_image: Any, cropped_image_height: int
):
    """
    This function crops the captured image to the area of interest.

    For the horizontal axis, it keeps the whole width of the image:

        x0 = 0  --->  x1 = constants.camera_frame_width

    For the vertical axis, it keeps the middle 80px of the image:

        y0 = camera_frame_height/2 - cropped_image_height/2  ---->  y1 = y0 + cropped_image_height

    """

    # We select the x limits
    x_axis_start = 0
    x_axis_end = x_axis_start + camera_frame_width

    # We select the y limits
    y_axis_start = int((camera_frame_height / 2) - (cropped_image_height / 2))
    y_axis_end = y_axis_start + cropped_image_height

    return raw_captured_image[y_axis_start:y_axis_end, x_axis_start:x_axis_end]


def draw_band_lines_on_display_image(cropped_image: Any, camera_frame_width: int, cv2: Any, halfway_height_px: int):
    """
    We visually display the 3px band that will be used for wavelength intensity
    calculations. We draw two lines, each 1px away from the band limits, to visually display
    where we are carrying out measurements in the image
    """

    cv2.line(
        cropped_image,
        (0, halfway_height_px - 2),
        (camera_frame_width, halfway_height_px - 2),
        (255, 255, 255),
        1,
    )
    cv2.line(
        cropped_image,
        (0, halfway_height_px + 2),
        (camera_frame_width, halfway_height_px + 2),
        (255, 255, 255),
        1,
    )


def draw_graticule_on_display_image(
    cv2: Any,
    static_elements: dict,
    gui_font: Any,
    graticule_data_dict: dict,
    text_offset: int,
    camera_frame_width: int,
):
    """
    Draws a graticule on the display image using the provided graticule_data_dict.
    This includes vertical lines at regular wavelength intervals and horizontal lines for intensity reference.
    Labels are added at major wavelength steps.
    """

    # Draw vertical lines every 10nm (minor graticule)
    for px_index in graticule_data_dict["ten_step_pxs"]:
        cv2.line(
            static_elements["graph"],
            (px_index, 15),
            (px_index, 320),
            (200, 200, 200),
            1,
        )

    # Draw vertical lines and labels every 50nm (major graticule)
    for px_index, wavelength_value_label in graticule_data_dict["fifty_step_pxs_with_label"]:
        cv2.line(static_elements["graph"], (px_index, 15), (px_index, 320), (0, 0, 0), 1)
        cv2.putText(
            static_elements["graph"],
            str(wavelength_value_label) + "nm",
            (px_index - text_offset, 12),
            gui_font,
            0.4,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )

    # Draw horizontal lines every 64px (intensity reference)
    for i in range(320):
        if i >= 64 and i % 64 == 0:  # skip the first line, then draw at each 64px step
            cv2.line(
                static_elements["graph"],
                (0, i),
                (camera_frame_width, i),
                (100, 100, 100),
                1,
            )


def draw_colored_spectrogram(cv2: Any, static_elements: dict, gui_font: Any, state_manager: SpectrometerStateManager):
    """
    Draw the spectral intensity graph as colored vertical lines
    Creates a visual representation of the spectrum where each pixel column becomes a vertical line with:
        - color based on the wavelength at that position
        - height proportional to the intensity at that position
    """

    calibration_data = state_manager.get_calibration_data()
    min_dist_betw_peaks = state_manager.get_minimum_distance_betw_peaks()
    intensity_array = state_manager.get_intensity_array()
    threshold = state_manager.get_threshold()

    px_to_wavelength_array = calibration_data["px_to_wavelength_array"]

    index = 0
    for intsty in intensity_array:
        rgb = wavelength_to_rgb(int(px_to_wavelength_array[index]))  # derive the color from the px_to_wavelength_array map
        r = rgb["R"]
        g = rgb["G"]
        b = rgb["B"]

        # Draw the main line and a black border on top
        cv2.line(static_elements["graph"], (index, 320), (index, 320 - intsty), (b, g, r), 1)
        cv2.line(
            static_elements["graph"],
            (index, 319 - intsty),
            (index, 320 - intsty),
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )
        index += 1

    # find peaks and label them
    text_offset = 12
    indexes = find_peaks_in_array(
        values_array=intensity_array, threshold=threshold / max(intensity_array), min_dist_betw_peaks=min_dist_betw_peaks
    )

    for i in indexes:
        height = intensity_array[i]
        height = 310 - height
        wavelength = round(float(px_to_wavelength_array[i]), 1)
        cv2.rectangle(
            static_elements["graph"],
            ((i - text_offset) - 2, height),
            ((i - text_offset) + 60, height - 15),
            (0, 255, 255),
            -1,
        )
        cv2.rectangle(
            static_elements["graph"],
            ((i - text_offset) - 2, height),
            ((i - text_offset) + 60, height - 15),
            (0, 0, 0),
            1,
        )
        cv2.putText(
            static_elements["graph"],
            str(wavelength) + "nm",
            (i - text_offset, height - 3),
            gui_font,
            0.4,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )
        # flagpoles
        cv2.line(static_elements["graph"], (i, height), (i, height + 10), (0, 0, 0), 1)


def show_wavelength_at_mouse_position(
    cv2: Any,
    static_elements: dict,
    gui_font: Any,
    state_manager: SpectrometerStateManager,
):
    """
    Displays the wavelength at the mouse position when measuring mode is active.
    It draws a crosshair cursor and shows the wavelength value aligned with the pixel position
    for easier identification.
    """
    calibration_data = state_manager.get_calibration_data()

    cursor_x, cursor_y = state_manager.get_mouse_position()
    px_to_wavelength_array = calibration_data["px_to_wavelength_array"]

    # When are_we_measuring is True, it displays an interactive crosshair cursor that shows the wavelength at the mouse position.
    if state_manager.is_measuring_mode_active():
        # show the cursor!
        cv2.line(
            static_elements["graph"],
            (cursor_x, cursor_y - 140),
            (cursor_x, cursor_y - 180),
            (0, 0, 0),
            1,
        )
        cv2.line(
            static_elements["graph"],
            (
                cursor_x - 20,
                cursor_y - 160,
            ),
            (
                cursor_x + 20,
                cursor_y - 160,
            ),
            (0, 0, 0),
            1,
        )
        cv2.putText(
            static_elements["graph"],
            str(round(float(px_to_wavelength_array[cursor_x]), 2)) + "nm",
            (
                cursor_x + 5,
                cursor_y - 165,
            ),
            gui_font,
            0.4,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )


def show_px_at_mouse_position_for_calibration(
    cv2: Any,
    static_elements: dict,
    gui_font: Any,
    state_manager: SpectrometerStateManager,
):
    """
    This section handles calibration mode - when the user is measuring pixel positions and
    recording clicks for spectrometer calibration.

    Also make sure the click array stays empty; when not in calibration mode, any previously recorded click positions become
    irrelevant and should be removed to prevent accidental calibration with old data.
    """

    cursor_x, cursor_y = state_manager.get_mouse_position()

    if state_manager.is_calibration_mode_active():
        # display the points
        cv2.line(
            static_elements["graph"],
            (cursor_x, cursor_y - 140),
            (cursor_x, cursor_y - 180),
            (0, 0, 0),
            1,
        )
        cv2.line(
            static_elements["graph"],
            (
                cursor_x - 20,
                cursor_y - 160,
            ),
            (
                cursor_x + 20,
                cursor_y - 160,
            ),
            (0, 0, 0),
            1,
        )
        cv2.putText(
            static_elements["graph"],
            str(cursor_x) + "px",
            (
                cursor_x + 5,
                cursor_y - 165,
            ),
            gui_font,
            0.4,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )
    else:
        state_manager.clear_calibration_clicks()  # clear the click array when not in calibration mode


def draw_clicks_as_circles(cv2: Any, static_elements: dict, state_manager: SpectrometerStateManager):
    """
    Display calibration reference points on the spectrum graph.
    For each stored click in the click array, it draws a circle and the pixel position.
    Purpose: to help the user see where they clicked and what pixel position they recorded during calibration.
    """

    click_array = state_manager.get_click_array()

    if click_array:
        for data in click_array:
            mouse_x = data[0]
            mouse_y = data[1]
            cv2.circle(static_elements["graph"], (mouse_x, mouse_y), 5, (0, 0, 0), -1)
            # we can display text :-) so we can work out wavelength from x-pos and display it ultimately
            cv2.putText(
                static_elements["graph"],
                str(mouse_x),
                (mouse_x + 5, mouse_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 0, 0),
            )


def stack_images_and_display_spectrum(
    cv2: Any,
    static_elements: dict,
    cropped_image: Any,
    gui_font: Any,
    camera_frame_width: int,
    state_manager: SpectrometerStateManager,
    spectrograph_win_name: str,
):
    """
    Gommills: this docstring was AI generated and I didn't have time to review it yet.
    ---
    Assembles and displays the complete spectrometer GUI by stacking visual elements and overlaying status information.

    This function creates the main spectrometer display by vertically stacking three key components:
    1. Banner image (top section with branding/title)
    2. Cropped camera image (middle section showing the spectral band)
    3. Spectrum graph (bottom section with the colored intensity visualization)

    It then overlays real-time status information in two columns on the composite image:
    - Left column: Calibration status, polynomial fit type, save status, and camera gain
    - Right column: Peak hold status, Savgol filter settings, peak detection parameters

    Finally displays the complete assembled image in the specified OpenCV window.

    Args:
        cv2: OpenCV module for image operations and text rendering
        static_elements: Dictionary containing pre-rendered UI components:
            - "banner_image": Top banner with title/branding
            - "graph": Bottom spectrum visualization with colored intensity bars
        cropped_image: The cropped camera frame showing the spectral band of interest
        gui_font: OpenCV font object for text rendering
        camera_frame_width: Width of the camera frame in pixels (used for positioning elements)
        state_manager: SpectrometerStateManager instance providing access to:
            - Calibration data and status messages
            - Camera settings (gain)
            - Processing parameters (threshold, filter settings, peak detection)
            - Save operation status
            - Peak hold mode status
        spectrograph_win_name: Name of the OpenCV window to display the assembled image

    Returns:
        numpy.ndarray: The complete assembled spectrum_vertical image array that was displayed

    Side Effects:
        - Displays the assembled image in the specified OpenCV window via cv2.imshow()
        - Draws white dividing lines between the stacked image sections
        - Overlays cyan-colored status text on the composite image

    Note:
        Text positioning is hardcoded with specific pixel coordinates:
        - Left column starts at x=15, right column at x=145
        - Text lines are spaced 18 pixels apart vertically (y=15, 33, 51, 69)
        - All status text uses cyan color (0, 255, 255) for consistency
    """
    calibration_data = state_manager.get_calibration_data()
    calibration_messages = calibration_data["calibration_messages"]

    picam_gain = state_manager.get_camera_gain()
    are_we_holding_peaks_msg = state_manager.get_peak_hold_status_message()
    are_we_calibrating = state_manager.is_calibration_mode_active()
    threshold = state_manager.get_threshold()
    savgol_filter_poly = state_manager.get_savgol_filter_poly()
    minimum_distance_betw_peaks = state_manager.get_minimum_distance_betw_peaks()

    # stack the images and display the spectrum
    spectrum_vertical = np.vstack((static_elements["banner_image"], cropped_image, static_elements["graph"]))
    # dividing lines...
    cv2.line(spectrum_vertical, (0, 80), (camera_frame_width, 80), (255, 255, 255), 1)
    cv2.line(spectrum_vertical, (0, 160), (camera_frame_width, 160), (255, 255, 255), 1)

    first_column_messages = [
        f"Mode: {state_manager.get_spectrometer_mode()}",
        calibration_messages["calibration_status"],
        f"Camera gain: {str(picam_gain)}",
        f"Are we calibrating?: {str(are_we_calibrating)}",
    ]
    second_column_messages = [
        are_we_holding_peaks_msg,
        "Savgol Filter: " + str(savgol_filter_poly),
        "Min Distance Betw Peaks: " + str(minimum_distance_betw_peaks),
        "Label Threshold: " + str(threshold),
    ]

    for i, message in enumerate(first_column_messages):
        cv2.putText(
            spectrum_vertical,
            message,
            (15, 15 + i * 18),
            gui_font,
            0.4,
            (0, 255, 255),
            1,
            cv2.LINE_AA,
        )

    for i, message in enumerate(second_column_messages):
        cv2.putText(
            spectrum_vertical,
            message,
            (230, 15 + i * 18),
            gui_font,
            0.4,
            (0, 255, 255),
            1,
            cv2.LINE_AA,
        )

    cv2.imshow(spectrograph_win_name, spectrum_vertical)

    return spectrum_vertical


def generate_graticule_for_gui(px_to_wavelength_array: Any) -> dict[str, list[int | tuple[int, int]]]:
    """
    Generate graticule lines for the spectrometer GUI display.

    Creates vertical reference lines at regular wavelength intervals (every 10nm and 50nm)
    within the measurement range limits, aligned with the actual calibration data to ensure
    accurate positioning on the spectrum display.

    Args:
        px_to_wavelength_array: Array mapping pixel indices to wavelength values from calibration

    Returns:
        dict: Dictionary containing pixel positions for graticule lines and labels
    """
    lowest_wavelength = px_to_wavelength_array[0]
    highest_wavelength = px_to_wavelength_array[-1]

    # Round wavelength limits and add margin for complete coverage
    lowest_wavelength_limit = int(round(lowest_wavelength)) - 10
    highest_wavelength_limit = int(round(highest_wavelength)) + 10

    graticule_lines_dict: dict[str, list] = {}

    # Generate 10nm interval lines - find pixel positions for wavelengths divisible by 10
    ten_step_lines_px_positions = []
    for wvlng in range(lowest_wavelength_limit, highest_wavelength_limit):
        if wvlng % 10 == 0:
            # Found a wavelength that is a multiple of 10nm within the range.
            # To align the graticule with the actual data, find the pixel index
            # whose wavelength value is closest to this target using the minimum absolute difference.
            px_index, wavelength_real_value = min(enumerate(px_to_wavelength_array), key=lambda x: abs(wvlng - x[1]))

            # Only include lines where the closest match is within 1nm (avoids spurious lines)
            if abs(wvlng - wavelength_real_value) < 1:
                ten_step_lines_px_positions.append(px_index)

    graticule_lines_dict["ten_step_pxs"] = ten_step_lines_px_positions

    # Generate 50nm interval lines with labels - these will show wavelength values
    fifty_step_lines_px_positions_with_label = []
    for wvlngth in range(lowest_wavelength_limit, highest_wavelength_limit):
        if wvlngth % 50 == 0:
            # Find pixel index aligned with actual calibration data
            px_index, wavelength_real_value = min(enumerate(px_to_wavelength_array), key=lambda x: abs(wvlngth - x[1]))

            # Only include labels where the match is within 1nm accuracy
            if abs(wvlngth - wavelength_real_value) < 1:
                wavelength_value_label = int(round(wavelength_real_value))
                label_data = (px_index, wavelength_value_label)
                fifty_step_lines_px_positions_with_label.append(label_data)

    graticule_lines_dict["fifty_step_pxs_with_label"] = fifty_step_lines_px_positions_with_label

    return graticule_lines_dict
