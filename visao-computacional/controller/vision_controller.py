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

            # Processando as faces detectadas
            faces = self._process_faces(rekognition_faces)

            # Obtendo metadados da imagem e URL assinada
            metadata = self.s3_service.get_image_metadata(self.bucket, self.image_name)
            image_url = self.s3_service.get_signed_url(self.bucket, self.image_name)
            creation_time = metadata['LastModified'].strftime('%d-%m-%Y %H:%M:%S')
            
            response = {
                'url_to_image': image_url,
                'created_image': creation_time,
                'faces': faces,
                'pets': pet_labels
            }

            # Adicionar informações de pets caso tenha detectado algum
            if pet_labels["pets"]:
                pets = self._process_pets(pet_labels)
                response['pets'] = pets
                logger(f'Pets encontrados: {pets}')
            else:
                response['pets'] = []
                logger(f'Nenhum pet encontrado na imagem')

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
            # Gera logs de faces encontradas na imagem
            logger(f'Faces encontradas: {faces}')
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
            # Gera logs de faces não encontradas na imagem 
            logger(f'Nenhuma face encontrada na imagem')

        return faces

    def _process_pets(self, pet_labels):
        pets = []
        filtered_breeds = ['Animal', 'Pet', 'Dog', 'Bird', 'Mammal', 'Vertebrate', 'Canidae','Canine', 'Carnivore', 'Terrestrial animal', 'Dog breed', 'Dog like mammal']
        unique_breeds = {breed['Name']: breed for pet in pet_labels["pets"] for breed in pet["labels"] if breed['Name'] not in filtered_breeds}.values()

        logger(f'Raças únicas: {unique_breeds}') # Gera o log das raças únicas detectadas pelo Rekognition

        for breed in unique_breeds: # Para cada raça de animal de estimação detectada pelo Rekognition
            self.bedrock_service.set_pet_breed(breed['Name'])
            response = self.bedrock_service.invoke_model()
            if response['statusCode'] == 200:
                tips = json.loads(response['Dicas'])
            else:
                tips = 'Erro ao obter dicas do Bedrock'

            pet_info = {
                'labels': [{'Confidence': breed['Confidence'], 'Name': breed['Name']}],
                'Dicas': tips
            }
            pets.append(pet_info)

        return pets
