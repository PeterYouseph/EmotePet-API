import boto3

s3 = boto3.client('s3')

def get_image_metadata(bucket, image_name): # Função para obter os metadados de uma imagem no S3 e retornar o objeto de metadados
    metadata = s3.head_object(Bucket=bucket, Key=image_name)
    return metadata

def get_signed_url(bucket, image_name): # Função para gerar uma URL assinada para acessar a imagem no S3
    url = s3.generate_presigned_url('get_object',
                                    Params={'Bucket': bucket, 'Key': image_name},
                                    ExpiresIn=3600)
    return url
