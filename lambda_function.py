"""Module for Lambda handler for secret rotation"""
import boto3

from alb_listener_modifier import ALBListenerModifier
from cf_token_refresher import CFTokenRefresher


def lambda_handler(event, context):

    """Lambda handler function"""

    arn = event["SecretId"]
    token = event["ClientRequestToken"]
    step = event["Step"]

    # Setup the client
    service_client = boto3.client("secretsmanager")

    # Make sure the version is staged correctly
    metadata = service_client.describe_secret(SecretId=arn)
    if not metadata["RotationEnabled"]:
        raise ValueError(f"Secret {arn} is not enabled for rotation")

    if step == "createSecret":
        create_secret(service_client, arn, token)

    elif step == "setSecret":
        set_secret(service_client, arn, token)

    elif step == "testSecret":
        test_secret(service_client, arn, token)

    elif step == "finishSecret":
        finish_secret(service_client, arn, token)

    else:
        raise ValueError("Invalid step parameter")


def create_secret(service_client, arn, token):

    """Function to create a new secret"""

    # Now try to get the secret version, if that fails, put a new secret
    try:
        service_client.get_secret_value(
            SecretId=arn, VersionId=token, VersionStage="AWSPENDING"
        )
    except service_client.exceptions.ResourceNotFoundException:
        # Generate a new token
        new_token = service_client.get_random_password(
            ExcludePunctuation=True, PasswordLength=32
        )
        # Put the secret
        service_client.put_secret_value(
            SecretId=arn,
            ClientRequestToken=token,
            SecretString=new_token["RandomPassword"],
            VersionStages=["AWSPENDING"],
        )


def set_secret(service_client, arn, token):
    """set the new token in cloudflare and application load balancer"""

    # retrieve the old secret
    old_token = service_client.get_secret_value(SecretId=arn, VersionStage="AWSCURRENT")
    # retrieve the new secret
    new_token = service_client.get_secret_value(SecretId=arn, VersionStage="AWSPENDING")
    print(new_token['SecretString'])

    # Change token in cloudflare
    print("Rotating the token in cloudflare...")
    token_refresh = CFTokenRefresher()
    response = token_refresh.roll_token(new_token['SecretString'])
    print(response.json())

    # Modify the token in the listener rule
    print("Modifying ELB listener rule with two token values...")
    modify_listener = ALBListenerModifier()
    modify_listener.modify_rule([old_token['SecretString'], new_token['SecretString']])


def test_secret(service_client, arn, token):

    """Method to test the new token."""

    print("No need to testing against any service...")


def finish_secret(service_client, arn, token):
    """Method to set the Version stage of the new token."""

    # First describe the secret to get the current version
    metadata = service_client.describe_secret(SecretId=arn)

    for version in metadata["VersionIdsToStages"]:
        if "AWSCURRENT" in metadata["VersionIdsToStages"][version]:
            if version == token:
                # The correct version is already marked as current, return
                return

            # Finalize by staging the secret version current
            service_client.update_secret_version_stage(
                SecretId=arn,
                VersionStage="AWSCURRENT",
                MoveToVersionId=token,
                RemoveFromVersionId=version,
            )
            # Retrieve the new token from the secret manager
            print("Retrieving new token from secret manager...")
            current_token = service_client.get_secret_value(
                SecretId=arn, VersionStage="AWSCURRENT"
            )
            print(current_token['SecretString'])
            # Updating listener rule and removing the old token
            print("Updating the ELB listener rule with only the new token...")
            modify_listener = ALBListenerModifier()
            modify_listener.modify_rule([current_token['SecretString']])
            break
