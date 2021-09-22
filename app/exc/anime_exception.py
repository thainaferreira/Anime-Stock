class AnimeNotFoundError(Exception):
    message = {
        "error": "Not Found"
    }


class AnimeAlreadExistsError(Exception):
    message = {
        "error": "anime is already exists"
    }


class KeyError(Exception):
    ...