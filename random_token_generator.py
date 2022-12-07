import random
import string

"""Random token generator class"""


class RandomTokenGenerator:
    def generate_random_token(self):
        # return "".join(random.choice(string.hexdigits) for _ in range(50))
        return "".join(random.choice(string.hexdigits) for _ in range(30))
