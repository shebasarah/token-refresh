"""Cloudflare API call"""

import requests
from random_token_generator import RandomTokenGenerator
from get_api_key import GetAPIKey
from store_token_SM import SaveToken

# CF_API_KEY = "Vhd7lE-isSY5QobG3k5eVCHYy87mjn9G0Kv19lTK"
CF_ZONE_ID = "72bab892f6318efaa9451b6fa18b9a26"
CF_RULE_ID = "b3ac5edd385a47f2827bd62d9dd923d0"


class TokenRefresh:
    """Token refresh class"""

    # roll cloudflare token secret
    def roll_token(self):
        """Generate token"""
        random_token_generator = RandomTokenGenerator()
        token = random_token_generator.generate_random_token()
        print(token)

        """Get CF_API_KEY"""
        CF_API_KEY = GetAPIKey.get_secret()
        print(CF_API_KEY)

        """Modify Token for Http Request Header"""
        response = requests.put(
            f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/rulesets/phases/http_request_late_transform/entrypoint",
            headers={
                "Authorization": f"Bearer {CF_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "rules": [
                    {
                        "id": CF_RULE_ID,
                        "description": "X-WAF-SECRET",
                        "expression": '(http.host ne "1")',
                        "action": "rewrite",
                        "action_parameters": {
                            "headers": {
                                "X-WAF-SECRET": {
                                    "operation": "set",
                                    "value": token,
                                },
                            },
                        },
                        "enabled": True,
                    },
                ],
            },
            timeout=10,
        )
        print(response.status_code)
        print(response.json())
        result = None

        if response:
            data = response.json()
            if response.status_code == 200:
                result = data

                """If response 200, save new token in secret manager"""
                save_token = SaveToken()
                save_token_response = save_token.save_token(token)
                print(save_token_response)

        return result
