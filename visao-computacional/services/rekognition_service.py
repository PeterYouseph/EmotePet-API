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
 
    # Função para detectar rótulos em uma imagem no S3 e retornar os detalhes dos rótulos
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

    # Função para identificar características dos animais de estimação na resposta do Rekognition
    def animal_characteristics(self, rekognition_response):
        pet_labels = ['Dog', 'Cat', 'Bird', 'Fish', 'Reptile', 'Mammal', 'Pet'] # Lista de rótulos de possíveis animais de estimação
        animal_characteristics = []
        for label in rekognition_response["Labels"]: # Para cada rótulo detectado na imagem
            for parent in label["Parents"]: # Para cada rótulo pai do rótulo atual (se houver)
                if parent.get("Name") in pet_labels:
                    animal_characteristics.append(label)
        return animal_characteristics

    # Função para detectar animais de estimação e suas raças em uma imagem no S3 e retornar os detalhes dos animais de estimação
    def detect_pets(self, bucket, image_name):
        labels_response = self.detect_labels(bucket, image_name)
        animal_characteristics = self.animal_characteristics(labels_response)
        pets = self.pets_labels_treatment(animal_characteristics)
        return pets

    def pets_labels_treatment(self, animal_characteristics): # Função para tratar os rótulos dos animais de estimação
        animal_dict = {"pets": []}  # Inicializa um dicionário para armazenar os animais de estimação detectados
        set_pets = set()  # Inicializa um conjunto para armazenar os nomes dos animais de estimação detectados sem repetição

        for label in animal_characteristics: # Para cada rótulo de animal de estimação detectado
            if label['Name'] not in set_pets: # Se o nome do animal não foi visto ainda
                set_pets.add(label['Name'])  # Adiciona o nome do animal ao conjunto de nomes vistos
                animal_dict["pets"].append({
                    "labels": [{
                        "Confidence": label['Confidence'],
                        "Name": label['Name']
                    }]
                })

        return animal_dict
