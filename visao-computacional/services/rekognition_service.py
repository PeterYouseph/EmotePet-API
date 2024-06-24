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
        MaxLabels=10
    )
    return response
