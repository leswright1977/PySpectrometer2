from typing import Any


def write_calibration_data(click_array_from_cv2: Any, calibration_data_file_path: str) -> bool:

    pixels_int_list = []
    wavelengths_float_list = []

    # Enter known wavelengths for observed pixels!
    for i in click_array_from_cv2:
        pixel = i[0]

        wv_is_valid = False
        while not wv_is_valid:
            inputted_wavelength_str = input("Enter wavelength for: " + str(pixel) + "px:")
            try:
                inputted_wavelength_float = float(inputted_wavelength_str)
                break
            except Exception:
                continue

        pixels_int_list.append(pixel)
        wavelengths_float_list.append(inputted_wavelength_float) # type: ignore

    pxdata = ",".join(map(str, pixels_int_list))  # convert array to string
    wldata = ",".join(map(str, wavelengths_float_list))  # type: ignore # convert array to string
    
    with open(calibration_data_file_path, "w") as file:
        file.write(pxdata + "\r\n")
        file.write(wldata + "\r\n")
        return True
    
    return False
