"""Cloudflare API call"""

import requests
from random_token_generator import RandomTokenGenerator
from get_api_key import GetAPIKey

CF_API_KEY = "Vhd7lE-isSY5QobG3k5eVCHYy87mjn9G0Kv19lTK"
CF_ZONE_ID = "72bab892f6318efaa9451b6fa18b9a26"
CF_RULE_ID = "b3ac5edd385a47f2827bd62d9dd923d0"


class TokenRefresh:
    """Token refresh class"""

    # roll cloudflare token secret
    def roll_secret(self):
        """Generate token"""
        random_token_generator = RandomTokenGenerator()
        token = random_token_generator.generate_random_token()
        """Get key"""
        # key = GetAPIKey.get_secret()
        # print(key)
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
        # print(response.status_code)
        # print(response.json())
        # result = None

        if response:
            data = response.json()
            print(response.status_code)
            # print(data)

            if response.status_code == 200:
                result = data

        return result
