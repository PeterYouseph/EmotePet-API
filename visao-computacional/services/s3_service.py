import boto3

class S3Service:
    def __init__(self):
        self.s3 = boto3.client('s3')

    # Função para obter os metadados de uma imagem no S3 e retornar o objeto de metadados
    def get_image_metadata(self, bucket, image_name):
        metadata = self.s3.head_object(Bucket=bucket, Key=image_name)
        return metadata

    # Função para gerar uma URL para acessar a imagem no S3
    def get_signed_url(self, bucket, image_name):
        url = self.s3.generate_presigned_url('get_object',
                                             Params={'Bucket': bucket, 'Key': image_name},
                                             ExpiresIn=3600)
        return url
