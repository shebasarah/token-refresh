from cloudflare_api_call import TokenRefresh

"""Modifying token in Http Request Header"""

if __name__ == "__main__":
    token_refresh = TokenRefresh()
    secret = token_refresh.roll_secret()

    print(secret)
