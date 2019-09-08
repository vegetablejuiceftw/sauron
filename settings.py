SERVO_TIMEOUT = 20.0

CONFIG = dict(
    default=[
        dict(
            descriptor='camera_opencv:CameraOpenCV',
            index=2,
            half_broadcast=False,
            camera_sleep=0.013,
            cap_fps=59,
        ),
        dict(
            descriptor='web_server:launch',
            frame_buffer_name="shm://camera",
            workers=1,
        ),
        dict(
            descriptor='detector:Detector',
            zoom=1,
        ),
        dict(
            descriptor='autonomous:Autonomous',
            autonomous_timeout=0.70,
        ),
        dict(
            descriptor='servo:Servo',
            timeout=SERVO_TIMEOUT,
            driver="arduino",
        ),
    ],
    color=[
        dict(
            descriptor='camera_opencv:CameraOpenCV',
            index=0,
            half_broadcast=False,
            camera_sleep=0.013,
            cap_fps=59,
        ),
        dict(
            descriptor='web_server:launch',
            frame_buffer_name="shm://camera-masked",
            workers=1,
        ),
        dict(
            descriptor='detector_color:Detector',
            zoom=1,
            lower=[29, 60, 56],
            upper=[81, 144, 173],
        ),
    ],
    raspberry=[
        dict(
            # probably other camera provider
            descriptor='camera_opencv:CameraOpenCV',
            index=0,
            half_broadcast=False,
            camera_sleep=0.029,
            cap_fps=30,
        ),
        dict(
            descriptor='web_server:launch',
            frame_buffer_name="shm://camera",
            workers=1,
        ),
        dict(
            descriptor='detector:Detector',
            zoom=1,
        ),
        dict(
            descriptor='autonomous:Autonomous',
            autonomous_timeout=1.0,
        ),
        dict(
            descriptor='servo:Servo',
            timeout=SERVO_TIMEOUT,
            driver="arduion",  # could use the pan tilt hat, but it has power draw issues :/
        ),
    ],
    image_only=[
        dict(
            descriptor='camera_opencv:CameraOpenCV',
            index=0,
            half_broadcast=False,
            camera_sleep=0.016,
            cap_fps=59,
        ),
        dict(
            descriptor='web_server:launch',
            frame_buffer_name="shm://camera",
            workers=1,
        ),
        dict(
            descriptor='detector:Detector',
            zoom=1,
        ),
    ],
)
