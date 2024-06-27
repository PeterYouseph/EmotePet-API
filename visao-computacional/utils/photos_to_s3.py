import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def upload_image_to_s3(image_name, bucket_name, object_name=None):

    """
    Faz o upload de uma imagem para o bucket no S3

    image_name: imagem a ser enviada
    object_name: nome do objeto no S3. Se none, image é usado
    bucket_name: bucket para onde a imagem será enviada
    return: True se o upload foi bem sucedido, False caso contrário
    """

    if object_name is None:
        object_name = image_name

    s3_client = boto3.client('s3')

    try:
        # Verifica se a imagem está presente no bucket
        s3_client.head_object(Bucket=bucket_name, Key=object_name)
        print(f"O arquivo {object_name} já existe no bucket {bucket_name}")
        return False

    except ClientError as e:
        # Se não existir, a exceção é lançada e o código continua
        error_code = e.response['Error']['Code']

        if error_code == '404':
            # objeto não existe no bucket então faz o upload
            try: 
                s3_client.upload_file(image_name, bucket_name, object_name)
                print(f"Arquivo {object_name} enviado com sucesso para o bucket {bucket_name}")
                return True    
            except NoCredentialsError:
                print("Credenciais não encontradas")
                return False
        else:
            # Outros erros
            print(f"Erro ao tentar o objeto {object_name} no bucket {bucket_name}: {error_code}")
            return False