import json

import boto3


def insert_json_into_dynamodb(json_data, table_name):
    # Cria uma conexão com o DynamoDB
    dynamodb = boto3.resource('dynamodb')

    # Obtém a referência para a tabela
    table = dynamodb.Table(table_name)
    json_response = json.loads(json_data)

    # Insere os dados JSON na tabela
    table.put_item(Item=json_response)