import json


def openJason(path):
    if(path is None):
        with open('instance.json', 'r') as arquivo:
            dados = json.load(arquivo)
    else:
        with open(path, 'r') as arquivo:
            dados = json.load(arquivo)

    return dados;

def recordJson(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file)

    json.dump(data, file, indent=4)
