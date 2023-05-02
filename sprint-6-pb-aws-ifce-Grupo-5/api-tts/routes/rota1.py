import json
import os

import boto3
from functions.pollyRequest import polly_to_s3


def v1_tts(event, context):
    # Carregar o corpo da requisição como um dicionário
    body = json.loads(event.get('body', '{}'))
    
    # Recuperar os dados enviados na requisição
    key = body.get('key', [])
    data = body.get('phrase', [])
    if key=='749abaa6a1d2a2aa894a5d711b951eb8':
        json_response=polly_to_s3(data)

        response = {
                    "statusCode": 200,
                    "body": json_response
                }
    else:
        body = {
        "Erro": "Chave de segurança incorreta ou inexistente, certifique-se se o seu JSON possui o campo key!"
        }

        response = {"statusCode": 500, "body": json.dumps(body)}
    
                

    
    return response