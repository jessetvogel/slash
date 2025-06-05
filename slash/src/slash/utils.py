import random
import string


# TODO: Pseudo-random while guaranteeing uniqueness
# IDEA: The unit group of a field of size N = 2^n is cyclic, so find a generator!
def random_id() -> str:
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return "_" + "".join(random.choices(characters, k=8))
