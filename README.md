# _The ever watchful eye._

Features
- shared memory computer vision workflow
- brokerless message queue for pubsub
- mutli stage face recognition, including focusing only on ROI speedup
- web server for video camera streaming and input broadcasting

Services
- web_server.py - camera streaming and input broadcasting
- servo.py - pan & tilt servo hat control, smooth motion
- camera_X.py - camera worker to generate camera stream, X = [opencv, picamera]
- detector.py - detect faces from video stream
- autonomous.py - use detection data to plan tracking
