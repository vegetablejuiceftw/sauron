SERVO_TIMEOUT = 20.0

CONFIG = dict(
    default=[
        dict(
            descriptor='camera_opencv:CameraOpenCV',
            index=0,
            half_broadcast=False,
            camera_sleep=0.013,
            cap_fps=59,
        ),
        dict(
            descriptor='web_server:launch',
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
            descriptor='asgi_web_server:launch',
            workers=1,
        ),
        dict(
            descriptor='detector:Detector',
            zoom=1,
        ),
    ],
)
