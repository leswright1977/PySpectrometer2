from typing import Any
import time
import os

def save_snapshot_of_current_spectrogram(
        save_data: dict,
        cv2: Any,
        snapshot_folder: str = "storage/snapshots"
        ) -> str:
    """
    Save spectral image, optional waterfall image, and data CSV with timestamp into storage/.
    
    Parameters:
        savedata (tuple): (spectrum_image, (wavelengths, intensities), [optional_waterfall_image])
    
    Returns:
        str: Timestamp message of last save.
    """

    # Data to store:
    time_stamp = time.strftime("%Y%m%d--%H%M%S")
    timenow = time.strftime("%H:%M:%S")
    spectrum_vertical = save_data["spectrum_vertical"]
    px_to_wavelength_array = save_data["px_to_wavelength_array"]
    intensity_array = save_data["intensity_array"]

    # Store the data, folder is from main.py's path resolution, so, from the root folder of the program:
    csv_file_path = os.path.join(snapshot_folder, "spectrum-" + time_stamp + ".csv")
    image_file_path = os.path.join(snapshot_folder, "spectrum-" + time_stamp + ".png")

    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

    cv2.imwrite(image_file_path, spectrum_vertical)
    with open(csv_file_path, "x") as f:
        f.write("Wavelength,Intensity\r\n")
        for x in zip(px_to_wavelength_array, intensity_array):
            f.write(str(x[0]) + "," + str(x[1]) + "\r\n")
    message = "Last Save: " + timenow
    return message