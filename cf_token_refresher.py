"""Module is to make an API call to roll the cloudflare WAF token in the HTTP Request Header Modification rule"""

import requests

from get_api_key import GetAPIKey


CF_ZONE_ID = "a3342f271086830570f2a3e7fcc6c398"
CF_RULSET_ID = "1b276dd187ff40a8aafac3ba4aa6ae59"
CF_RULE_ID = "6b8a929b584a4086b050baae6ce1a725"


class CFTokenRefresher:
    """Cloudflare WAF token refresher class"""

    # roll cloudflare token secret
    def roll_token(self, token):
        """Roll token method"""

        # Get the cloudflare API key to access cloudflare
        cf_api_key = GetAPIKey.get_secret(self)

        # Modify Token for Http Request Header
        response = requests.patch(
            f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/rulesets/{CF_RULSET_ID}/rules/{CF_RULE_ID}",
            headers={
                "Authorization": f"Bearer {cf_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "action": "rewrite",
                "expression": '(http.host ne "1")',
                "description": "X-ALB-SECRET",
                "enabled": True,
                "action_parameters": {
                    "headers": {"X-ALB-SECRET": {"operation": "set", "value": token}}
                },
            },
            timeout=10,
        )
        return response
