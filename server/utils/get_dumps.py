import requests
import os

def get_dumps():
    # Cria o diretorio de dumps se ele não existir
    os.makedirs(os.environ["TANAKAI_DUMPS"], exist_ok=True)

    # Define as permissões do diretorio de dumps
    os.chmod(os.environ["TANAKAI_DUMPS"], 0o755)

    # Cria a lista de dumps disponiveis
    dumps_list = [
        "https://raw.githubusercontent.com/ao-data/ao-bin-dumps/refs/heads/master/items.xml",
        "https://raw.githubusercontent.com/ao-data/ao-bin-dumps/refs/heads/master/mobs.xml",
        "https://raw.githubusercontent.com/ao-data/ao-bin-dumps/refs/heads/master/harvestables.xml",
    ]

    # Faz o download dos dumps
    for dump in dumps_list:
        response = requests.get(dump)
        with open(f"{os.environ["TANAKAI_DUMPS"]}/{dump.split('/')[-1]}", "wb") as file:
            file.write(response.content)