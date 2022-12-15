"""Get Cloudflare API Key from Secret manager"""
import boto3
from botocore.exceptions import ClientError


class GetAPIKey:
    """Class to Get the API Key to access cloudflare."""

    def get_secret(self):
        """Method to get the API Key."""

        secret_name = "sheba_CF_API_Key"
        region_name = "ap-southeast-2"

        # """Create an STS client object that represents a live connection to the STS service"""
        # sts_client = boto3.client("sts")

        # """Call the assume_role method of the STSConnection object and pass the role ARN and a role session name"""
        # assumed_role_object = sts_client.assume_role(
        #     RoleArn="arn:aws:iam::490768973769:role/nzh-developer-access",
        #     RoleSessionName="AssumeRoleSession1",
        # )
        # print(assumed_role_object)

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
