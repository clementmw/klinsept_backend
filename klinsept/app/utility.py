# helper functions will include otp generation

import random
import string

def generate_otp():
    characters = string.ascii_letters + string.digits
    otp = ''.join(random.choices(characters,k=7))
    # print(otp)
    return otp

# generate_otp()


