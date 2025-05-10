import requests


def check_server_online(server):
    try:
        response = requests.get(server)

        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False
