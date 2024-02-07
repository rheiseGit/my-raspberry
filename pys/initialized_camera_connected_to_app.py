"""
This module instanciate an instance of class CameraControl in order 
to allow different pages to access the same instance.
It can be import where this instance is needed.
The instance of CameraControl is connected to the Flask-Server of the dash-app.
"""

import pys.camera as camera
from flask import Response
from dash import get_app
import json

with open("config.json") as json_data_file:
    configdata = json.load(json_data_file)

print("CONFIG.JSON")
print(configdata)

print("CAMERA INIT")
if configdata["camera"] == "PICAMERA":
    adapter = camera.AdapterPiCamera(0)
elif configdata["camera"] == "OPENCV":
    adapter = camera.AdapterOpenCV()
else:
    pass

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
