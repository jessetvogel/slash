import random
import string


def random_id() -> str:
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return "_" + "".join(random.choices(characters, k=8))
