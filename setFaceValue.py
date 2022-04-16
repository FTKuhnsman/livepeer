import requests
import time

while True:
    
    files = {
        'facevaluelimit': (None, '3000000000000000'),
    }
    
    response = requests.post('http://127.0.0.1:7935/setFaceValueLimit', files=files)
    
    time.sleep(60)