"""Module for Lambda handler for secret rotation"""
import boto3
from botocore.exceptions import ClientError
import requests


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
    region_name = "ap-southeast-2"
    secret_name = "sheba_CF_API_Key"

    # retrieve the old secret
    old_token = service_client.get_secret_value(SecretId=arn, VersionStage="AWSCURRENT")
    # retrieve the new secret
    new_token = service_client.get_secret_value(SecretId=arn, VersionStage="AWSPENDING")

    # Change token in cloudflare
    print("Rotating the token in cloudflare...")
    cf_zone_id = "72bab892f6318efaa9451b6fa18b9a26"
    cf_rule_id = "b3ac5edd385a47f2827bd62d9dd923d0"

    # Get the cloudflare API key to access cloudflare
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as error:
        raise error

        # Decrypts secret using the associated KMS key
    cf_api_key = get_secret_value_response["SecretString"]

    # Modify Token for Http Request Header
    response = requests.put(
        f"https://api.cloudflare.com/client/v4/zones/{cf_zone_id}/rulesets/phases/http_request_late_transform/entrypoint",
        headers={
            "Authorization": f"Bearer {cf_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "rules": [
                {
                    "id": cf_rule_id,
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
    print(response.json())

    # Modify the token in the listener rule
    print("Modifying ELB listener rule with two token values...")

    # Create secret manager client
    session = boto3.session.Session()
    client = session.client(service_name="elbv2", region_name=region_name)
    try:
        response = client.modify_rule(
            RuleArn="arn:aws:elasticloadbalancing:ap-southeast-2:177970211836:listener-rule/app/sheba-loadbalancer/38a97bd60a7d8892/44531f4d8ead8087/526eb7337545c69d",
            Conditions=[
                {
                    "Field": "http-header",
                    "HttpHeaderConfig": {
                        "HttpHeaderName": "X-WAF-SECRET",
                        "Values": [old_token, new_token],
                    },
                },
            ],
        )
        print(response)
    except ClientError as error:
        raise error


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
            print(current_token)
            # Updating listener rule and removing the old token
            print("Updating the ELB listener rule with only the new token...")
            region_name = "ap-southeast-2"

            # Create secret manager client
            session = boto3.session.Session()
            client = session.client(service_name="elbv2", region_name=region_name)
            try:
                response = client.modify_rule(
                    RuleArn="arn:aws:elasticloadbalancing:ap-southeast-2:177970211836:listener-rule/app/sheba-loadbalancer/38a97bd60a7d8892/44531f4d8ead8087/526eb7337545c69d",
                    Conditions=[
                        {
                            "Field": "http-header",
                            "HttpHeaderConfig": {
                                "HttpHeaderName": "X-WAF-SECRET",
                                "Values": current_token,
                            },
                        },
                    ],
                )
                print(response)
            except ClientError as error:
                raise error
            break
