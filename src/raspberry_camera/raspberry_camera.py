from picamera2 import Picamera2

def set_up_camera(
        camera_frame_width: int, 
        camera_frame_height: int,
        frame_duration_limit: tuple[int, int]) -> Picamera2:
    """
    2.- Raspberry camera interface set and initialized as picam2 (standard library's recommendation).
        The general pattern is:
            a) create camera object Picamera2
            b) create configuration and append it to this camera object
            Here we create a config for video recording.
    """
    
    picam2 = Picamera2()
    video_config = picam2.create_video_configuration(    
        main={"format": "RGB888", "size": (camera_frame_width, camera_frame_height)},
        controls={"FrameDurationLimits": frame_duration_limit},
    )
    picam2.configure(video_config)
    picam2.start()

    return picam2