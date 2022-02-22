from requests import get


def saveImageFromUrl(url: str, path: str = "./") -> None:
    response = get(url)
    with open(path, "wb") as file:
        file.write(response.content)
