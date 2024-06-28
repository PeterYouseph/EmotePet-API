import boto3
import json
from botocore.exceptions import ClientError

""""
Caso for testar o Bedrock veja se está habilitado o modelo no AWS Bedrock (https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess)
"""

class BedrockClass:
    def __init__(self):
        # Inicia a sessão do Boto3
        self.session = boto3.Session(region_name='us-east-1')

        # Inicia o serviço Bedrock
        self.bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

    def verify_credentials(self):
        try:
            sts_client = self.session.client('sts')
            identity = sts_client.get_caller_identity()
            print("AWS credentials are valid.")
            print(f"Account: {identity['Account']}, UserID: {identity['UserId']}, ARN: {identity['Arn']}")
        
        except ClientError as e:
            print(f"Error verifying credentials: {e}")
            return False
        return True
    
    def set_dog_breed(self, dog_race):
        self.dog_race = dog_race
        return True