import requests

r = requests.get("http://localhost:5698/buddies", params={"auth": "903c7dc3-8de2-4746-9846-ae48b16fb006"})
print(r.content)
print(r.status_code)