from typing import Any

from src.state_manager.state_manager import SpectrometerStateManager
from src.config.config import UserConfiguration


def set_up_open_cv_display(
    state_manager: SpectrometerStateManager,
    user_config: UserConfiguration,
    cv2: Any,
) -> None:
    DISP_FULL_SCREEN = user_config.runtime_config.disp_full_screen
    SPECTROGRAPH_WIN_NAME = user_config.constants.spectrograph_win_name
    CAMERA_FRAME_WIDTH = user_config.constants.camera_frame_width
    STACK_HEIGHT = user_config.constants.stack_height

    if DISP_FULL_SCREEN is True:
        cv2.namedWindow(SPECTROGRAPH_WIN_NAME, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(
            SPECTROGRAPH_WIN_NAME,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_FULLSCREEN,
        )
    else:
        cv2.namedWindow(SPECTROGRAPH_WIN_NAME, cv2.WINDOW_GUI_NORMAL)
        cv2.resizeWindow(
            SPECTROGRAPH_WIN_NAME,
            CAMERA_FRAME_WIDTH,
            STACK_HEIGHT,
        )
        cv2.moveWindow(SPECTROGRAPH_WIN_NAME, 0, 0)

    # Here we track the mouse in the cv window
    param_tuple = (state_manager, cv2)
    cv2.setMouseCallback(
        SPECTROGRAPH_WIN_NAME,
        _handle_mouse_events_in_cv_window,
        param_tuple,
    )


def _handle_mouse_events_in_cv_window(event: int, x: int, y: int, flags, param):
    """
    Handle mouse events for the OpenCV window.

    Tracks the current mouse position and records left-click positions,
    adjusting for a vertical offset in the coordinate system.

    Args:
        event (int): The type of mouse event (e.g., movement, click).
        x (int): The x-coordinate of the mouse event.
        y (int): The y-coordinate of the mouse event.
        flags (int): Any relevant flags passed by OpenCV.
        param (any): Additional parameters (not used here).

    Behavior:
        - On mouse move, updates cursorX and cursorY from mouse_events_variables
        - On left button click, appends the click position (with vertical offset subtracted)
          to click_array.
    """

    mouse_y_offset = 160
    state_manager, cv2 = param  # param is passed from cv2.setMouseCallback (not very elegant, but no other option...)
    if event == cv2.EVENT_MOUSEMOVE:
        state_manager.update_mouse_position(x, y)
    if event == cv2.EVENT_LBUTTONDOWN:
        mouseX = x
        mouseY = y - mouse_y_offset
        state_manager.add_calibration_click(mouseX, mouseY)
