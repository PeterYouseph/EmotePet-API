import boto3

class RekognitionService:
    def __init__(self):
        self.rekognition = boto3.client('rekognition')

    # Função para detectar faces em uma imagem no S3 e retornar os detalhes das faces
    def detect_faces(self, bucket, image_name):
        response = self.rekognition.detect_faces(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': image_name
                }
            },
            Attributes=['ALL']
        )
        return response

    # Função para detectar rótulos em uma imagem no S3
    def detect_labels(self, bucket, image_name):
        response = self.rekognition.detect_labels(
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

    # Função para detectar animais de estimação e suas raças em uma imagem no S3
    def detect_pets(self, bucket, image_name):
        labels_response = self.detect_labels(bucket, image_name) # Detecta os rótulos da imagem para identificar animais de estimação
        pets = []
        pet_types = ['Dog', 'Cat', 'Pet', 'Bird', 'Animal'] # Tipos de animais de estimação a serem considerados
        for label in labels_response['Labels']:
            if any(pet in label['Name'] for pet in pet_types): # Verifica se o rótulo é um animal de estimação
                pet_data = {
                    'type': label['Name'],
                    'confidence': label['Confidence'],
                    'breeds': []
                }
                for potential_breed in labels_response['Labels']: # Verifica se o rótulo é uma raça de animal de estimação
                    if any(parent['Name'] in pet_types for parent in potential_breed.get('Parents', [])):
                        pet_data['breeds'].append({
                            'breed': potential_breed['Name'],
                            'confidence': potential_breed['Confidence']
                        })
                pets.append(pet_data)
        if not pets: # Caso não encontre animais de estimação, retorna um objeto vazio
            pets = [{
                'type': None,
                'confidence': None,
                'breeds': []
            }]
        return pets
