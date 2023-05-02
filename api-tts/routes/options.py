import json


def tts_opt(event, context):
    with open('templates/index.html', 'r') as file:
        html_content = file.read()
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': html_content,
        }
    return response
    