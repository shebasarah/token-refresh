"""Get Cloudflare API Key from Secret manager"""
import boto3
from botocore.exceptions import ClientError


class GetAPIKey:
    """Class to Get the API Key to access cloudflare."""

    def get_secret(self):
        """Method to get the API Key."""

        secret_name = "nzh-cf-access-token-to-modify-transform-rules"
        region_name = "ap-southeast-2"

        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region_name)

        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        except ClientError as error:
            raise error

        # Decrypts secret using the associated KMS key
        secret = get_secret_value_response["SecretString"]
        return secret

