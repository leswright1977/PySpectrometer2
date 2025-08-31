from typing import Any
import numpy as np

def load_static_elements(cv2: Any, camera_frame_width: int) -> dict:
    """
    Loads static UI elements for display, including a banner image and a blank graph.
    Args:
        cv2 (Any): The OpenCV module.
        camera_settings (CameraSettings): An object containing camera configuration.
        background (str, optional): Base64-encoded string representing the banner image. Defaults to BACKGROUND.
    Returns:
        dict: A dictionary containing:
            - "banner_image": The decoded banner image as a NumPy array.
            - "graph": A blank white graph image as a NumPy array with dimensions [320, camera_frame_width, 3].
    """

    # Here we: 1.- decode the banner image 2.- convert it to an array 3.- add it to messages for display
    with open("src/gui/banner_image.png", "rb") as f:
        decoded_banner_image_data = f.read()
    # Convert the decoded image data to a NumPy array
    np_data = np.frombuffer(decoded_banner_image_data, np.uint8)
    banner_image = cv2.imdecode(np_data, 3)

    # blank image. Graph has specific proportions, one of which 320 is, but this is hardcoded (fix later)
    graph = np.zeros([320, camera_frame_width, 3], dtype=np.uint8)
    graph.fill(255)  # fill white

    static_elements = {"banner_image": banner_image, "graph": graph}

    return static_elements
