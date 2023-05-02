import json
import os

import boto3
from functions.hash import generate_short_id
from functions.pollyRequest import polly_to_s3
from functions.query import check_if_item_exists
from functions.upload import insert_json_into_dynamodb


def v3_tts(event, context):
    body = json.loads(event.get('body', '{}'))
    
    # Recuperar os dados enviados na requisição
    key = body.get('key', [])
    data = body.get('phrase', [])

    
    json_hash = {"unique_id": generate_short_id(data)}
    
    if key=='749abaa6a1d2a2aa894a5d711b951eb8':
        if check_if_item_exists('json_table',generate_short_id(data))==False:
            json_response = polly_to_s3(data)
            json_response = json.loads(json_response)  
            json_response.update(json_hash)
            json_response=json.dumps(json_response)
            insert_json_into_dynamodb(json_response,'json_table')
            response = {
                            "statusCode": 200,
                            "body":json_response
                        }
        else:
            json_response=check_if_item_exists('json_table',generate_short_id(data))
            response = {"statusCode": 200, "body": json_response}
    else:
        body = {
        "Erro": "Chave de segurança incorreta ou inexistente, certifique-se se o seu JSON possui o campo key!"
        }

        response = {"statusCode": 500, "body": json.dumps(body)}
    return response
    