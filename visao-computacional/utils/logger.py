import boto3
import json
import datetime

logs = boto3.client('logs')

def logger(message): # Função para logar mensagens de informação no CloudWatch
    print(message)
    logs.put_log_events(
        logGroupName='rekognition-logs',
        logStreamName='vision-logs',
        logEvents=[ # Adiciona a mensagem de informação ao log de informações
            {
                'timestamp': int(datetime.datetime.now().timestamp() * 1000),
                'message': json.dumps(message)
            }
        ]
    )

def error(message): # Função para logar mensagens de erro no CloudWatch
    print(message)
    logs.put_log_events(
        logGroupName='rekognition-logs',
        logStreamName='vision-errors',
        logEvents=[ # Adiciona a mensagem de erro ao log de erros
            {
                'timestamp': int(datetime.datetime.now().timestamp() * 1000),
                'message': json.dumps(message)
            }
        ]
    )
