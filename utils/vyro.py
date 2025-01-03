import requests

url = 'https://api.vyro.ai/v2/image/edits/generative-fill'
headers = {
    'Authorization': 'Bearer vk-MJdEuxBquWaLugyhMQ9mxWCDSJDQGunySyQOQK5mi3NQ3',
}

files = {
    'prompt': (None, 'An autumn scene with leaves'),
    'image': ('file', open("/Users/antonshever/Desktop/original.png", 'rb')),
    'mask': ('file', open("/Users/antonshever/Desktop/mask.png", 'rb')),
}

response = requests.post(url, headers=headers, files=files)

print(response.json())
