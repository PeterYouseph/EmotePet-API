import json
from controller import vision_controller


def health(event, context): # Função para verificar a saúde da aplicação 
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }

    response = {"statusCode": 200, "body": json.dumps(body)} # Retorna a resposta com o código 200 e a mensagem de sucesso

    return response

def v1_description(event, context): # Função para retornar a descrição da API na versão 1
    body = {
        "message": "VISION api version 1."
    }

    response = {"statusCode": 200, "body": json.dumps(body)} # Retorna a resposta com o código 200 e a descrição da API

    return response

def v2_description(event, context): # Função para retornar a descrição da API na versão 2
    body = {
        "message": "VISION api version 2."
    }

    response = {"statusCode": 200, "body": json.dumps(body)} # Retorna a resposta com o código 200 e a descrição da API

    return response

def detect_faces(event, context): # Função para detectar faces em uma imagem
    body = json.loads(event['body'])
    bucket = body['bucket']
    image_name = body['imageName']

    try: # Tenta processar a imagem e detectar faces
        response = vision_controller.process_image(bucket, image_name)
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    except Exception as e:  # Em caso de erro, loga a exceção e retorna um erro 500
        error_message = f'Internal Server Error: {str(e)}'
        print(error_message)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': error_message})
        }

def detect_faces_and_pets(event, context): # Função para detectar faces e animais de estimação em uma imagem
    body = json.loads(event['body'])
    bucket = body['bucket']
    image_name = body['imageName']

    try: # Tenta processar a imagem e detectar faces e animais de estimação
        response = vision_controller.process_image_with_pets(bucket, image_name)
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    except Exception as e: # Em caso de erro, loga a exceção e retorna um erro 500
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal Server Error - {}'.format(str(e))})
        }