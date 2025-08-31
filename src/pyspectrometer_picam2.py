from pydantic import ValidationError
from typing import Any
import logging
import cv2


from src.capture_iteration.waterfall.capture_waterfall import capture_waterfall_iteration
from src.capture_iteration.transmittance.capture_transmittance_iteration import (
    capture_transmittance_iteration,
)
from src.capture_iteration.emittance.load_static import load_static_elements
from src.capture_iteration.emittance.capture_emittance_iteration import (
    capture_emittance_iteration,
)
from src.state_manager.state_manager import SpectrometerStateManager
from src.config.config_loader import load_and_validate_config
from src.gui.opencv_display import set_up_open_cv_display
from src.config.config import UserConfiguration


def start_spectrometer(config_path: str) -> None:
    return handle_user_input(config_path)


# (1/4) This function handles user input and starts the spectrometer application if and only if the configuration is valid.
def handle_user_input(config_path: str) -> None:
    logging.basicConfig(format="%(asctime)s - %(message)s", datefmt="%H:%M", level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        user_config = load_and_validate_config(config_path)
        logger.info("(1/4) Configuration loaded and validated successfully.")
    except ValidationError:
        return logger.error("(1/4) Configuration validation failed. Invalid configuration values.")
    except FileNotFoundError:
        return logger.error("(1/4) Configuration file not found. Please check the file path.")

    # Now that we have valid config, instantiate the spectrometer state manager. This contains
    # the constants and mutable variables of the spectrometer and methods to interact with both.
    state_manager = SpectrometerStateManager(
        camera_width=user_config.constants.camera_frame_width,
        default_calculus_params=user_config.state_defaults,
        testing_mode=user_config.runtime_config.testing_mode,
    )

    return start_camera(user_config=user_config, state_manager=state_manager)


# (2/4) This function sets up the RaspBerry camera object Picamera2
def start_camera(user_config: UserConfiguration, state_manager: SpectrometerStateManager) -> None:
    spectrometer_constants = user_config.constants

    if state_manager.is_testing_mode():
        logging.info("(2/4) Camera init skipped; testing mode.")
        picam2 = None
    else:
        from src.raspberry_camera.raspberry_camera import set_up_camera  # type: ignore

        try:
            picam2 = set_up_camera(
                camera_frame_width=spectrometer_constants.camera_frame_width,
                camera_frame_height=spectrometer_constants.camera_frame_height,
                frame_duration_limit=spectrometer_constants.frame_duration_limit,
            )
        except Exception as e:
            return logging.error(f"(2/4) Failed to set up camera: {e}")

        logging.info("(2/4) Camera initialized successfully.")

    return set_up_gui(user_config, state_manager, picam2)


# (3/4) This function sets up the GUI with OpenCV
def set_up_gui(user_config: UserConfiguration, state_manager: SpectrometerStateManager, picam2: Any = None) -> None:
    set_up_open_cv_display(cv2=cv2, user_config=user_config, state_manager=state_manager)

    logging.info("(3/4) OpenCV GUI set up successfully.")

    return initialize_capturing_loop(user_config, picam2, state_manager)


# (4/4) This function starts the capturing loop, which is the main loop of the spectrometer application.
def initialize_capturing_loop(
    user_config: UserConfiguration, picam2: Any | None, state_manager: SpectrometerStateManager
) -> None:
    constants = user_config.constants
    static_elements = load_static_elements(cv2=cv2, camera_frame_width=constants.camera_frame_width)

    logging.info("(4/4) About to start capturing loop.")

    return _capturing_loop(picam2=picam2, state_manager=state_manager, constants=constants, static_elements=static_elements)


def _capturing_loop(picam2: Any, state_manager: SpectrometerStateManager, constants: Any, static_elements: dict) -> None:
    spectrometer_on = True

    while spectrometer_on:
        running_mode = state_manager.get_spectrometer_mode()

        if running_mode == "emittance_spectrometer":
            spectrometer_on = capture_emittance_iteration(
                cv2=cv2, picam2=picam2, state_manager=state_manager, static_elements=static_elements, constants=constants
            )
        elif running_mode == "transmittance_spectrometer":
            spectrometer_on = capture_transmittance_iteration(
                cv2=cv2, picam2=picam2, state_manager=state_manager, static_elements=static_elements, constants=constants
            )
        elif running_mode == "waterfall_display":
            spectrometer_on = capture_waterfall_iteration(
                cv2=cv2, picam2=picam2, state_manager=state_manager, static_elements=static_elements, constants=constants
            )

    return cv2.destroyAllWindows()
