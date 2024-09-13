import cv2

for camera_id in range(10):
    try:
        camera = cv2.VideoCapture(camera_id)
        camera_info = cv2.VideoCapture(camera_id).getBackendName()
        frame_width = int(camera.get(3))
        frame_height = int(camera.get(4))
        frame_rate = camera.get(5)
        
        print(f"Camera ID: {camera_id}")
        print(f"Backend Name: {camera_info}")
        print(f"Resolution: {frame_width}x{frame_height}")
        print(f"Frame Rate: {frame_rate} fps")
    except Exception as e:
        print(f"{camera_id}: None")