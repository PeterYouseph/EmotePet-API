import boto3
import json
from botocore.exceptions import ClientError

""""
Caso for testar o Bedrock veja se está habilitado o modelo no AWS Bedrock (https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess)
"""

class BedrockService:
    def __init__(self):
        # Inicia a sessão do Boto3
        self.session = boto3.Session(region_name='us-east-1')

        # Inicia o serviço Bedrock
        self.bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
        
    def set_pet_breed(self, pet_breed): # Função para definir a raça do animal de estimação
        self.pet_breed = pet_breed
        return True

    # Cria um prompt detalhado sobre a raça do animal de estimação
    def create_prompt(self):
        prompt = f"""
        Escreva um texto detalhado sobre as características, cuidados e problemas de saúde comuns para a seguinte raça de Pet: {self.pet_breed}.

        Dicas sobre {self.pet_breed}: 
        Nível de Energia e Necessidades de Exercícios: 
        Temperamento e Comportamento: 
        Cuidados e Necessidades: 
        Problemas de Saúde Comuns:
        Informações Extras:
        """
        return prompt
     
    def generate_request_body(self):
       
        # Gera o corpo da requisição para enviar ao modelo, incluindo o prompt e configurações de geração de texto
        request_body = {
            "inputText": self.create_prompt(),
            "textGenerationConfig": {
                "maxTokenCount": 1000,
                "temperature": 0.1, # temperature:  aleatoriedade na geração de texto (quanto maior, mais aleatorio e menos conservador o texto é)
                "topP": 1 # topP:  tokens que compõem o top p% da probabilidade cumulativa
            },
        }
        return json.dumps(request_body)

    def invoke_model(self):
        model_id = "amazon.titan-text-express-v1"

        response = self.bedrock.invoke_model(modelId=model_id, body=self.generate_request_body())

        try:
            # Invoca o modelo com o corpo da requisição gerado
            response = self.bedrock.invoke_model(
                        modelId=model_id, 
                        contentType='application/json',
                        body=self.generate_request_body()
            )
            
            # Processa a resposta do modelo
            model_response = json.loads(response["body"].read().decode('utf-8'))

            response_text = model_response["results"][0]["outputText"]

            # Retorna a resposta formatada
            return {'statusCode': 200, 'Dicas': json.dumps(response_text, indent=4, ensure_ascii=False)}
        
        except ClientError as e:
            print(f"Error invoking model: {e}")
            return {'statusCode': 500, 'body': json.dumps(str(e))}    