import boto3

rekognition = boto3.client('rekognition')

def detect_faces(bucket, image_name): # Função para detectar faces em uma imagem no S3 e retornar os detalhes das faces
    response = rekognition.detect_faces(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': image_name
            }
        },
        Attributes=['ALL']
    )
    return response

def detect_labels(bucket, image_name): # Função para detectar rótulos em uma imagem no S3
    response = rekognition.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': image_name
            }
        },
        MaxLabels=10,
        MinConfidence=80
    )
    return response

def detect_pets(bucket, image_name): # Função para detectar animais de estimação e suas raças em uma imagem no S3
    labels_response = detect_labels(bucket, image_name)
    pets = []
    pet_types = ['Dog', 'Cat', 'Pet', 'Bird', 'Animal']
    for label in labels_response['Labels']:
        if any(pet in label['Name'] for pet in pet_types):
            pet_data = {
                'type': label['Name'],
                'confidence': label['Confidence'],
                'breeds': []
            }
            for potential_breed in labels_response['Labels']:
                # Verificar se é uma subcategoria de "Dog" ou "Cat"
                if any(parent['Name'] in pet_types for parent in potential_breed.get('Parents', [])):
                    pet_data['breeds'].append({
                        'breed': potential_breed['Name'],
                        'confidence': potential_breed['Confidence']
                    })
            pets.append(pet_data)
    if not pets:
        pets = [{
            'type': None,
            'confidence': None,
            'breeds': []
        }]
    return pets
