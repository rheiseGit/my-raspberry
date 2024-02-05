import pys.camera as camera
from flask import Response
from dash import get_app

"""
Camera is defined here in order to allow to access the same CameraController 
in several pages of the dash app
"""

print("CAMERA INIT")
adapter = camera.AdapterPiCamera(3)
cam = camera.CameraController(adapter=adapter)
res = cam.check()
print(" - CAMERA CHECK", res, id(cam))

# Endpoint for videofeed
app = get_app()


# Videostream via Flask
@app.server.route("/video_feed")
def video_feed():
    print("CREATION OF VIDEOFEED - CAMERACONTOL")
    return Response(
        camera.gen(cam), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


print("CAMERA INIT DONE")
