import json
from controller.vision_controller import VisionController

def health(event, context): 
    # Função para verificar a saúde da aplicação 
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }

    response = {"statusCode": 200, "body": json.dumps(body)} # Retorna a resposta com o código 200 e a mensagem de sucesso
    return response

def v1_description(event, context): 
    # Função para retornar a descrição da API na versão 1
    body = {
        "message": "VISION api version 1."
    }

    response = {"statusCode": 200, "body": json.dumps(body)} # Retorna a resposta com o código 200 e a descrição da API v1
    return response

def v2_description(event, context): 
    # Função para retornar a descrição da API na versão 2
    body = {
        "message": "VISION api version 2."
    }

    response = {"statusCode": 200, "body": json.dumps(body)} # Retorna a resposta com o código 200 e a descrição da API v2
    return response

def detect_faces(event, context):  
    # Função para detectar faces em uma imagem no S3 e retornar os detalhes
    if 'body' not in event: # Valida se há um body da requisição
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing body in request'})
        }

    body = json.loads(event['body'])
    bucket = body.get('bucket')
    image_name = body.get('imageName')

    if not bucket or not image_name: # Valida se o bucket e o nome da imagem estão presentes no body
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'bucket and imageName are required'})
        }

    try: 
        vision_controller = VisionController(bucket, image_name)
        response = vision_controller.process_image() # Chama a função para processar a imagem com pessoas e detectar faces e emoções
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    except Exception as e:  
        error_message = f'Internal Server Error: {str(e)}'
        print(error_message)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': error_message})
        }

def detect_faces_and_pets(event, context):  
    # Função para detectar faces e animais de estimação em uma imagem no S3 e retornar os detalhes
    if 'body' not in event: # Valida se há um body da requisição
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing body in request'})
        }

    body = json.loads(event['body'])
    bucket = body.get('bucket')
    image_name = body.get('imageName')

    if not bucket or not image_name: # Valida se o bucket e o nome da imagem estão presentes no body
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'bucket and imageName are required'})
        }

    try: 
        vision_controller = VisionController(bucket, image_name)
        response = vision_controller.process_image_with_pets() # Chama a função para processar a imagem com pessoas e Pets e detectar faces e emoções
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    except Exception as e: 
        error_message = f'Internal Server Error: {str(e)}'
        print(error_message)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': error_message})
        }
