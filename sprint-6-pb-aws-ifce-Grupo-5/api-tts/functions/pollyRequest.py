import datetime
import json
from datetime import timedelta

import boto3


def polly_to_s3(text):
    polly = boto3.client('polly')
    s3 = boto3.client('s3')

    bucket = 'polly-spint6'
    result = s3.list_objects(Bucket=bucket)
    count = result.get('Contents', [])

    response = polly.synthesize_speech(
        VoiceId='Ricardo',
        OutputFormat='mp3',
        Text=str(text)
    )

    s3.put_object(
        Body=response['AudioStream'].read(),
        Bucket='polly-spint6',
        Key='polly-'+str(len(count))+'.mp3'
    )

    url_full= s3.generate_presigned_url(
    ClientMethod='get_object',
    Params={
        'Bucket': bucket,
        'Key': 'polly-'+str(len(count))+'.mp3'
    })
    url = url_full.split('?')[0]
    

    brasilia_offset = timedelta(hours=-3)
    brasilia_time = datetime.datetime.utcnow() + brasilia_offset
    formatted_time = brasilia_time.strftime("%Y-%m-%d %H:%M:%S")

    dados = {
        "received_phrase": str(text),
        "url_to_audio": url,
        "created_audio": formatted_time
    }

    return json.dumps(dados)

