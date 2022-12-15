"""Module is to make an API call to roll the cloudflare WAF token in the HTTP Request Header Modification rule"""

import requests

from get_api_key import GetAPIKey


CF_ZONE_ID = "72bab892f6318efaa9451b6fa18b9a26"
CF_RULE_ID = "b3ac5edd385a47f2827bd62d9dd923d0"


class CFTokenRefresher:
    """Cloudflare WAF token refresher class"""

    # roll cloudflare token secret
    def roll_token(self, token):
        """Roll token method"""

        # Get the cloudflare API key to access cloudflare
        cf_api_key = GetAPIKey.get_secret(self)

        # Modify Token for Http Request Header
        response = requests.put(
            f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/rulesets/phases/http_request_late_transform/entrypoint",
            headers={
                "Authorization": f"Bearer {cf_api_key}",
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
