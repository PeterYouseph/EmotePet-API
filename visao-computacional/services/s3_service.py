import boto3

class S3Service:
    def __init__(self):
        self.s3 = boto3.client('s3')

    # Função para obter os metadados de uma imagem no S3 e retornar o objeto de metadados
    def get_image_metadata(self, bucket, image_name):
        metadata = self.s3.head_object(Bucket=bucket, Key=image_name)
        return metadata
        
    # Função para gerar uma URL pública para acessar a imagem no S3
    def get_signed_url(self, bucket, image_name):
        url = f'https://{bucket}.s3.amazonaws.com/{image_name}'
        return url
