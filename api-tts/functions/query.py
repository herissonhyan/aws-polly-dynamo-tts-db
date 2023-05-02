import json

import boto3


def check_if_item_exists(table_name, unique_id):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    response = table.get_item(
        Key={
            "unique_id": unique_id
        }
    )

    item = response.get("Item")
    if item:
        return json.dumps(item)
    else:
        return False
