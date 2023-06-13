import json

file = open("data.txt").read()
print(file[38-20:38+20])
d = json.dumps(["Lifestyles & Social Issues Portal | Britannica", "https://www.britannica.com/browse/Lifestyles-Social-Issues", "It\'s easy enough to agree that human beings all around the world have certain basic requirements that must be fulfilled in order to ensure their individual and collective well-being. History has shown..."])
print(d)
print(json.loads(d))
print()
print(json.loads(file))