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

    def list_models_available(self):
        bedrock_client = boto3.client('bedrock')
        list_models = [models['modelId'] for models in bedrock_client.list_foundation_models()['modelSummaries']]
        return list_models
        
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

    def invoke_model(self):
        model_id = "amazon.titan-text-express-v1"

        response = self.bedrock.invoke_model(modelId=model_id, body=self.generate_request_body())

        try:
            response = self.bedrock.invoke_model(
                        modelId=model_id, 
                        contentType='application/json',
                        body=self.generate_request_body()
            )
            
            model_response = json.loads(response["body"].read().decode('utf-8'))

            response_text = model_response["results"][0]["outputText"]

            return {'statusCode': 200, 'Dicas': json.dumps(response_text, indent=4, ensure_ascii=False)}
        
        except ClientError as e:
            print(f"Error invoking model: {e}")
            return {'statusCode': 500, 'body': json.dumps(str(e))}    