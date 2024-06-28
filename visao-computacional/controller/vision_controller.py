import json
from services.rekognition_service import RekognitionService
from services.s3_service import S3Service
from services.bedrock_service import BedrockService
from utils.logger import logger, error

class VisionController:
    def __init__(self, bucket, image_name):
        self.bucket = bucket
        self.image_name = image_name
        self.rekognition_service = RekognitionService()
        self.s3_service = S3Service()
        self.bedrock_service = BedrockService()
    
    # Função para processar uma imagem e detectar faces
    def process_image(self):
        try:
            # Detectando faces na imagem
            response_faces = self.rekognition_service.detect_faces(self.bucket, self.image_name)
            # Obtendo metadados da imagem e URL assinada
            metadata = self.s3_service.get_image_metadata(self.bucket, self.image_name)
            image_url = self.s3_service.get_signed_url(self.bucket, self.image_name)
            creation_time = metadata['LastModified'].strftime('%d-%m-%Y %H:%M:%S')

            # Processando as faces detectadas
            faces = self._process_faces(response_faces)

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

    # Função para processar uma imagem e detectar faces e animais de estimação
    def process_image_with_pets(self):
        try:
            # Detectando rótulos na imagem e filtrando animais de estimação
            pet_labels = self.rekognition_service.detect_pets(self.bucket, self.image_name)
            rekognition_faces = self.rekognition_service.detect_faces(self.bucket, self.image_name)
            logger(f'Rekognition data: {pet_labels}')

            # Processando as faces detectadas
            faces = self._process_faces(rekognition_faces)

            # Obtendo metadados da imagem e URL assinada
            metadata = self.s3_service.get_image_metadata(self.bucket, self.image_name)
            image_url = self.s3_service.get_signed_url(self.bucket, self.image_name)
            creation_time = metadata['LastModified'].strftime('%d-%m-%Y %H:%M:%S')

            response = {
                'url_to_image': image_url,
                'created_image': creation_time,
                'faces': faces
            }

            # Adicionar informações de pets caso tenha detectado algum
            if pet_labels:
                pets = self._process_pets(pet_labels)
                response['pets'] = pets
                print(f'Pets encontrados: {pets}')
            else:
                response['pets'] = []

            return response
        # Em caso de erro, loga a exceção e retorna
        except Exception as e:
            error(e)
            raise Exception('Internal Server Error')

    def _process_faces(self, response_faces):
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
        return faces

    def _process_pets(self, pet_labels): # Função para processar os rótulos de animais de estimação
        pets = []
        # Filtro de raças sem breeds que não são raças de animais de estimação:
        filtered_breeds = ['Animal', 'Pet', 'Dog', 'Bird', 'Mammal', 'Vertebrate', 'Canidae','Canine', 'Carnivore', 'Terrestrial animal', 'Dog breed', 'Dog like mammal']
        unique_breeds = {breed['breed']: breed for label in pet_labels for breed in label['breeds'] if breed['breed'] not in filtered_breeds}.values() # Filtra raças únicas
        print(f'Raças únicas: {unique_breeds}')

        for breed in unique_breeds: # Para cada raça única, chama o Bedrock para obter dicas e adiciona na lista de pets
            self.bedrock_service.set_pet_breed(breed['breed'])
            response = self.bedrock_service.invoke_model()
            if response['statusCode'] == 200: # Retorna as dicas do Bedrock caso a requisição tenha sido bem sucedida
                tips = json.loads(response['Dicas'])
            else:  # Caso contrário, retorna uma mensagem de erro
                tips = 'Erro ao obter dicas do Bedrock'

            pet_info = {
                'labels': [{'Confidence': breed['confidence'], 'Name': breed['breed']}],
                'Dicas': tips
            }
            pets.append(pet_info)

        return pets
