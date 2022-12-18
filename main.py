from cf_token_refresher import CFTokenRefresher
from random_token_generator import RandomTokenGenerator
from alb_listener_modifier import ALBListenerModifier
from store_token_SM import SaveToken
from get_curent_token import GetToken

"""Rotate token in secret manager, modify token in Http Request Header in Cloudflare and load balancer listener rule"""

if __name__ == "__main__":
    """Get Current token and save it in a variable"""
    print("Retrieving the current token...")
    old_token = GetToken.get_token()
    print(old_token)

    """Create new token"""
    print("Generating a new token...")
    random_token_generator = RandomTokenGenerator()
    new_token = random_token_generator.generate_random_token()
    print(f"The new token is {new_token}")
    print(
        "-----------------------------------------------------------------------------------------------------------------------------------------------------------"
    )
    """"Rotate token in secret manager"""
    print("Rotating the new token in to the secret manager...")
    save_token = SaveToken()
    save_token_response = save_token.save_token(new_token)
    # print(save_token_response)
    print(
        "-----------------------------------------------------------------------------------------------------------------------------------------------------------"
    )
    """Modify the token in the listener rule"""
    print("Modifying ELB listener rule with two token values...")
    modify_listener = ALBListenerModifier()
    modify_listener.modify_rule(old_token, new_token)
    print(
        "-----------------------------------------------------------------------------------------------------------------------------------------------------------"
    )
    """Retrieve the new token from the secret manager"""
    print("Retrieving new token from secret manager...")
    current_token = GetToken.get_token()
    print(current_token)
    print(
        "-----------------------------------------------------------------------------------------------------------------------------------------------------------"
    )
    """Change token in cloudflare"""
    print("Rotating the token in cloudflare...")
    token_refresh = CFTokenRefresher()
    response = token_refresh.roll_token(new_token)
    print(response.json())
    print(
        "-----------------------------------------------------------------------------------------------------------------------------------------------------------"
    )
    """Updating listener rule and removing the old token"""
    print("Updating the ELB listener rule with only the new token...")
    modify_listener.update_rule(current_token)
    print(
        "-----------------------------------------------------------------------------------------------------------------------------------------------------------"
    )
