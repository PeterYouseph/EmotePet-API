import boto3
import json
import datetime
from botocore.exceptions import ClientError

logs = boto3.client('logs')

def ensure_log_group(log_group_name): # Função para garantir que um grupo de logs exista no CloudWatch
    try: # Tenta criar um grupo de logs no CloudWatch
        logs.create_log_group(logGroupName=log_group_name) 
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
            print(f"Unexpected error: {e}")

def ensure_log_stream(log_group_name, log_stream_name): # Função para garantir que um fluxo de logs exista no CloudWatch
    try:  # Tenta criar um fluxo de logs no CloudWatch
        logs.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
            print(f"Unexpected error: {e}")

def log_message(log_group_name, log_stream_name, message): # Função para gerar logs de mensagens no CloudWatch em um grupo e fluxo de logs específicos
    ensure_log_group(log_group_name) # Garante que o grupo de logs 'rekognition-logs' exista no CloudWatch
    ensure_log_stream(log_group_name, log_stream_name) # Garante que o fluxo de logs 'vision-logs' exista no CloudWatch

    try:
        response = logs.describe_log_streams(
            logGroupName=log_group_name,
            logStreamNamePrefix=log_stream_name
        )

        sequence_token = None
        if 'logStreams' in response and len(response['logStreams']) > 0: # Verifica se o fluxo de logs 'vision-logs' existe no CloudWatch
            sequence_token = response['logStreams'][0].get('uploadSequenceToken', None) # Obtém o token de sequência do fluxo de logs 'vision-logs'

        log_event = { # Cria um evento de log com a mensagem de informação
            'logGroupName': log_group_name,
            'logStreamName': log_stream_name,
            'logEvents': [
                {
                    'timestamp': int(datetime.datetime.now().timestamp() * 1000), # Obtém o timestamp atual 
                    'message': json.dumps(message) # Converte a mensagem de informação para JSON
                }
            ]
        }
        
        if sequence_token:
            log_event['sequenceToken'] = sequence_token

        logs.put_log_events(**log_event)
    except ClientError as e:
        print(f"Failed to put log events: {e}")

def logger(message):  # Função para gerar logs com mensagens de informação no CloudWatch em caso de sucesso na requisição.
    print(message)
    log_message('rekognition-logs', 'vision-logs', message) # Loga a mensagem de informação no CloudWatch com o grupo de logs 'rekognition-logs' e o fluxo de logs 'vision-logs'

def error(message):  # Função para gerar logs de mensagens de erro no CloudWatch
    print(message)
    log_message('rekognition-logs', 'vision-errors', message) # Gera logs com a mensagem de erro no CloudWatch com o grupo de logs 'rekognition-logs' e o fluxo de logs 'vision-errors'
