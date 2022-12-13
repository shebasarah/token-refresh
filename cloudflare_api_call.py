"""Cloudflare API call"""

import requests
from random_token_generator import RandomTokenGenerator
from get_api_key import GetAPIKey
from store_token_SM import SaveToken
from modify_listener import ModifyListenerRule

# CF_API_KEY = "Vhd7lE-isSY5QobG3k5eVCHYy87mjn9G0Kv19lTK"
CF_ZONE_ID = "72bab892f6318efaa9451b6fa18b9a26"
CF_RULE_ID = "b3ac5edd385a47f2827bd62d9dd923d0"


class TokenRefresh:

    # roll cloudflare token secret
    def roll_token(self, token):
        """Generate token"""

        """Get CF_API_KEY"""
        CF_API_KEY = GetAPIKey.get_secret()
        # print(CF_API_KEY)

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
        return response
