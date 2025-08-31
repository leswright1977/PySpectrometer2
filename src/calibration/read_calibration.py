import numpy as np


def read_calibration_data(camera_frame_width: int, calibration_data_file_path: str) -> tuple[np.ndarray, dict[str, str]]:
    """
    Reads calibration data from 'caldata.txt', fits a polynomial to map pixel positions to wavelengths,
    and generates a wavelength array for the spectrometer image.

    The function supports both second-order (for 3 calibration points) and third-order (for >3 points) polynomial fitting.
    It also provides calibration status messages and, for third-order fits, calculates the R-squared value to assess fit quality.

    Args:
        camera_frame_width (int): The width of the camera frame (number of pixel columns).

    Returns:
        tuple: (
            px_to_wavelength_array (np.ndarray of float64): Wavelength value for each pixel column,
            calibration_messages (dict of messages)
        )

    Algorithm:
        1. Reads pixel positions and corresponding wavelengths from 'caldata.txt'.
        2. Validates calibration data; loads defaults if invalid or insufficient.
        3. Fits a polynomial (2nd or 3rd order) to the calibration points.
        4. Generates a wavelength value for each pixel column using the fitted polynomial.
        5. For >3 calibration points, calculates R-squared to assess fit quality.
        6. Returns the wavelength array and calibration status messages.
    """

    errors = 0
    calibration_messages: dict[str, str] = {}

    try:
        with open(calibration_data_file_path, "r") as file:
            # read both the pixel numbers line, which is the first, and the wavelengths line, the second one, and put them into two numpy arrays.
            lines = file.readlines()
            if not lines:
                raise FileNotFoundError("Calibration data file is empty.")

            pixels_raw_line = lines[0].strip()
            wavelengths_raw_line = lines[1].strip()
    except FileNotFoundError:
        # If the file does not exist, we load placeholder data
        pixels_raw_line = "0,400,800"
        wavelengths_raw_line = "380,560,750"
        errors = 1

    pixels_str_list = pixels_raw_line.split(",")
    pixels_int_array = np.array([int(i) for i in pixels_str_list if i], dtype=np.int32)

    wavelengths_str_list = wavelengths_raw_line.split(",")
    wavelengths_float_array = np.array([float(i) for i in wavelengths_str_list if i], dtype=np.float64)

    if len(pixels_int_array) != len(wavelengths_float_array):
        # The Calibration points are of unequal length!
        errors = 1
    if len(pixels_int_array) < 3 or len(wavelengths_float_array) < 3:
        # The Cal data contains less than 3 pixels or wavelengths!
        errors = 1

    if errors == 1:
        # Load placeholder data
        pixels_int_array = np.array([0, 400, 800], dtype=np.int32)
        wavelengths_float_array = np.array([380, 560, 750], dtype=np.float64)

    # create an array for the computed wavelengths (pixel-to-wavelength mapping)
    px_to_wavelength_array: np.ndarray = np.zeros(camera_frame_width, dtype=np.float64)

    if len(pixels_int_array) == 3:
        _second_order_polynomial_fit(
            errors=errors,
            pixels_array=pixels_int_array,
            camera_frame_width=camera_frame_width,
            wavelengths_array=wavelengths_float_array,
            calibration_messages=calibration_messages,
            px_to_wavelength_array=px_to_wavelength_array,
        )

    if len(pixels_int_array) > 3:
        _third_order_polynomial_fit(
            pixels_array=pixels_int_array,
            camera_frame_width=camera_frame_width,
            wavelengths_array=wavelengths_float_array,
            calibration_messages=calibration_messages,
            px_to_wavelength_array=px_to_wavelength_array,
        )
    
    print(calibration_messages)

    return (px_to_wavelength_array, calibration_messages)  # type: ignore


def _second_order_polynomial_fit(
    errors: int,
    pixels_array: np.ndarray,
    wavelengths_array: np.ndarray,
    camera_frame_width: int,
    calibration_messages: dict,
    px_to_wavelength_array: np.ndarray,
) -> None:
    # "Calculating second order polynomial..."
    coefficients = np.poly1d(np.polyfit(pixels_array, wavelengths_array, 2))
    C1 = coefficients[2]
    C2 = coefficients[1]
    C3 = coefficients[0]

    # Generate wavelength map
    for pixel in range(camera_frame_width):
        wavelength_calculated_value = (C1 * pixel**2) + (C2 * pixel) + C3
        wavelength_calculated_value = round(wavelength_calculated_value, 6)
        px_to_wavelength_array[pixel] = wavelength_calculated_value

    if errors == 1:
        calibration_messages["calibration_status"] = "R^2: 0"
        calibration_messages["which_points_we_used"] = "Placeholders loaded"
        calibration_messages["type_of_poly_fit"] = "Perform Calibration!"
    else:
        calibration_messages["calibration_status"] = "R^2: N/A"
        calibration_messages["which_points_we_used"] = "Using 3 calibration points"
        calibration_messages["type_of_poly_fit"] = "2nd Order Polyfit"
        # this alerts that only 3 wavelengths is inaccurate


def _third_order_polynomial_fit(
    pixels_array: np.ndarray,
    wavelengths_array: np.ndarray,
    camera_frame_width: int,
    calibration_messages: dict,
    px_to_wavelength_array: np.ndarray,
) -> None:
    # Calculating third order polynomial...
    coefficients = np.poly1d(np.polyfit(pixels_array, wavelengths_array, 3))

    C1 = coefficients[3]
    C2 = coefficients[2]
    C3 = coefficients[1]
    C4 = coefficients[0]

    # Generating Wavelength Data
    for pixel in range(camera_frame_width):
        wavelength = (C1 * pixel**3) + (C2 * pixel**2) + (C3 * pixel) + C4
        wavelength = round(wavelength, 6)
        px_to_wavelength_array[pixel] = wavelength

    # final job, we need to compare all the recorded wavelengths with predicted wavelengths
    predicted_wavelengths_temp = []

    # iterate over the original pixelnumber array and predict results
    for px in pixels_array:
        y = (C1 * px**3) + (C2 * px**2) + (C3 * px) + C4
        predicted_wavelengths_temp.append(y)

    # Convert to numpy array for consistency
    predicted_wavelengths_with_calibration_data = np.array(predicted_wavelengths_temp, dtype=np.float64)

    # calculate 2 squared of the result
    # if this is close to 1 we are all good!
    correlation_matrix = np.corrcoef(wavelengths_array, predicted_wavelengths_with_calibration_data)
    correlation = float(correlation_matrix[0, 1])
    r_square = float(correlation**2)

    calibration_messages["calibration_status"] = f"R^2: {float(r_square):.5f}"
    calibration_messages["which_points_we_used"] = f"Using {len(pixels_array)} cal points"
    calibration_messages["type_of_poly_fit"] = "3rd Order Polyfit"
