import json
from services.rekognition_service import detect_faces, detect_labels
from services.s3_service import get_image_metadata, get_signed_url
from services.bedrock_service import get_pet_tips
from utils.logger import logger, error
# Função para processar uma imagem e detectar faces
def process_image(bucket, image_name): 
    try: 
        # Detectando faces na imagem
        response_faces = detect_faces(bucket, image_name)
        # Obtendo metadados da imagem e URL assinada
        metadata = get_image_metadata(bucket, image_name)
        image_url = get_signed_url(bucket, image_name)
        creation_time = metadata['LastModified'].strftime('%d-%m-%Y %H:%M:%S')

        # Processando as faces detectadas
        faces = []
        if 'FaceDetails' in response_faces:
            for faceDetail in response_faces['FaceDetails']:
                face = {
                    "position": {
                        "Height": float(faceDetail["BoundingBox"]["Height"]),
                        "Left": float(faceDetail["BoundingBox"]["Left"]),
                        "Top": float(faceDetail["BoundingBox"]["Top"]),
                        "Width": float(faceDetail["BoundingBox"]["Width"])
                    },
                    "classified_emotion": faceDetail["Emotions"][0]["Type"],
                    "classified_emotion_confidence": float(faceDetail["Emotions"][0]["Confidence"])
                }
                faces.append(face)
        # Se não houver faces detectadas, retorna um objeto com valores nulos
        if not faces:
            faces = [{
                "position": {
                    "Height": None,
                    "Left": None,
                    "Top": None,
                    "Width": None
                },
                "classified_emotion": None,
                "classified_emotion_confidence": None
            }]
        # Montando a resposta da requisição com os dados processados
        response_body = {
            "url_to_image": image_url,
            "created_image": creation_time,
            "faces": faces
        }

        return response_body
    # Em caso de erro, loga a exceção e retorna
    except Exception as e:
        error(e)
        raise Exception('Internal Server Error')

def process_image_with_pets(bucket, image_name): # Função para processar uma imagem e detectar faces e animais de estimação
    try:
        # Detectando rótulos na imagem
        rekognition_labels = detect_labels(bucket, image_name)
        rekognition_faces = detect_faces(bucket, image_name)
        logger(f'Rekognition data: {rekognition_labels}')

        # Filtrando rótulos para identificar animais de estimação
        pet_labels = [label for label in rekognition_labels['Labels'] if 'Animal' in label['Categories'][0]['Name'] or 'Pets' in label['Categories'][0]['Name']]

        # Processando as faces detectadas
        faces = []
        if 'FaceDetails' in rekognition_faces:
            for face in rekognition_faces['FaceDetails']:
                emotion = max(face['Emotions'], key=lambda x: x['Confidence'])
                faces.append({
                    'position': {
                        "Height": float(face['BoundingBox']['Height']),
                        "Left": float(face['BoundingBox']['Left']),
                        "Top": float(face['BoundingBox']['Top']),
                        "Width": float(face['BoundingBox']['Width'])
                    },
                    'classified_emotion': emotion['Type'],
                    'classified_emotion_confidence': float(emotion['Confidence'])
                })

        # Obtendo metadados da imagem e URL assinada
        metadata = get_image_metadata(bucket, image_name)
        image_url = get_signed_url(bucket, image_name)
        creation_time = metadata['LastModified'].strftime('%d-%m-%Y %H:%M:%S')

        response = {
            'url_to_image': image_url,
            'created_image': creation_time,
            'faces': faces
        }
        # Adicionar informações de faces caso não tenha detectado nenhuma
        if not faces:
            response['faces'] = [{
                "position": {
                    "Height": None,
                    "Left": None,
                    "Top": None,
                    "Width": None
                },
                "classified_emotion": None,
                "classified_emotion_confidence": None
            }]

        # Adicionar informações de pets caso tenha detectado algum
        if pet_labels:
            pet_tips = get_pet_tips(pet_labels)
            response['pets'] = [{
                'labels': [{'Name': label['Name'], 'Confidence': float(label['Confidence'])} for label in pet_labels],
                'Dicas': pet_tips
            }]
        else:
            response['pets'] = []

        return response
    # Em caso de erro, loga a exceção e retorna
    except Exception as e:
        error(e)
        raise Exception('Internal Server Error')
