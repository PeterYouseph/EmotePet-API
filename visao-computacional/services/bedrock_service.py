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

    def create_prompt(self):
        prompt = f"""
        Escreva um texto detalhado sobre as características, cuidados e problemas de saúde comuns para a seguinte raça de cachorro: {self.dog_race}.

        Dicas sobre {self.dog_race}: 
        Nível de Energia e Necessidades de Exercícios: 
        Temperamento e Comportamento: 
        Cuidados e Necessidades: 
        Problemas de Saúde Comuns:
        Informações Extras:
        """
        return prompt
     
    def generate_request_body(self):
        # temperature:  aleatoriedade na geração de texto (quanto maior, mais aleatorio e menos conservador o texto é)
        # topP:  tokens que compõem o top p% da probabilidade cumulativa
        request_body = {
            "inputText": self.create_prompt(),
            "textGenerationConfig": {
                "maxTokenCount": 1000,
                "temperature": 0.1, 
                "topP": 1
            },
        }
        return json.dumps(request_body)
