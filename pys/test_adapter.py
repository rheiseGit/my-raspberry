import camera as c
import time

"""
print('-'*10)
adapter = c.AdapterPiCamera()
img = adapter.read()
print(type(img))
adapter.release()

time.sleep(2)
print('-'*10)
adapter2 = c.AdapterPiCamera()
img = adapter2.read()
print(type(img))
adapter2.release()

time.sleep(2)
"""

print('-'*10)
adapter3 = c.AdapterPiCamera()
videocam = c.VideoCamera(adapter=adapter3)
img = videocam.get_next_frame()
print(type(img))
