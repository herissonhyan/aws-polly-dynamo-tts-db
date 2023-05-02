# Realizar a conversão de texto para áudio utilizando *text to speech* e salvá-lo em um banco de dados.

## Sumário
* [Objetivo](#objetivo)
* [Ferramentas](#ferramentas)
* [Desenvolvimento](#desenvolvimento)
  * [Arquitetura serverless](#estrutura-serverless)
  * [Funções](#funções)
    * [Criação do hash](#hash)
    * [Conexão Polly com S3](#polly-para-s3)
    * [Conexão com o DynamoDB](#upload-para-o-dynamodb)
    * [Checagem de ID no DynamoDB](#checagem-de-id-no-dynamodb)
  * [Rotas](#rotas)
  * [Resultado](#resultado)
  * [Conclusão](#conclusão)
  * [Autores](#autores)

## Objetivo

Realizar a conversão de texto para áudio utilizando *text to speech* e salvá-lo em um banco de dados.

***

## Ferramentas

* [AWS](https://aws.amazon.com/pt/) plataforma de computação em nuvem da Amazon.
  * [Polly](https://aws.amazon.com/polly/) funcionalidade ideal para sintetizar discurso a partir de texto em uma variedade de vozes e idiiomas.
  * [DynamoDB](https://aws.amazon.com/dynamodb/) banco de dados não relacional que oferece rápida e escalável performance.
  * [S3](https://aws.amazon.com/s3/) serviço de armazenamento.
  * [API Gateway](https://aws.amazon.com/api-gateway/) serviço para criação, implantação e gerenciamento de APIs.
  * [Lambda](https://aws.amazon.com/lambda/) serviço de computação *serverless* que permite a execução de código sem a preocupação de gerenciar servidores.

***

## Desenvolvimento

### Estrutura serverless

```yml
service: api-tts
frameworkVersion: '3'

provider:
  name: aws
  runtime: python3.9

functions:
  health:
    handler: handler.health
    events:
      - httpApi:
          path: /
          method: get
  v1Description:
    handler: handler.v1_description
    events:
      - httpApi:
          path: /v1
          method: get
  v2Description:
    handler: handler.v2_description
    events:
      - httpApi:
          path: /v2
          method: get
  v1_tts:
    handler: routes/rota1.v1_tts
    events:
      - http:
          path: v1/tts
          method: post
  v2_tts:
    handler: routes/rota2.v2_tts
    events:
      - http:
          path: v2/tts
          method: post
  v3_tts:
    handler: routes/rota3.v3_tts
    events:
      - http:
          path: v3/tts
          method: post
  options:
    handler: routes/options.tts_opt
    events:
      - http:
          path: /options
          method: get
```

O [arquivo YAML](https://github.com/Compass-pb-aws-2022-IFCE/sprint-6-pb-aws-ifce/blob/Grupo-5/api-tts/serverless.yml) define uma aplicação *serverless* na AWS utilizando o serviço de *text-to-speech*.

O bloco de *functions* que definem o serviço de TTS, sendo elas:
* **health** retorna uma resposta em JSON ao ser acionada pelo método GET no caminho raiz "/".
* **v1Description**, **v2Description**, e **v3Description** são acionadas por um GET para os endpoints **/v1**, **/v2**, **/v3** respectivamente.
* Já as funções **v1_tts**, **v2_tts**, e **v3_tts** são ativadas pelo método POST para as rotas **/v1/tts**, **/v2/tts**, e **/v3/tts**.
* Por fim, a rota **options** se refere a página principal onde o texto será inserido e enviado para uma das rotas acima.

## Funções

### Hash

Para a criação do ID da frase inserida pelo usuário é utilizado uma função que converte o texto utilizando ho hash SHA-256.

O resultado do hash é uma representação binária, então é selecionado os 8 primeiros bits para serem convertidos em hexadecimal, que serve como um identificador único para o texto inserido.

```py
import hashlib

def generate_short_id(phrase):
    # Codificar a frase em bytes
    phrase_bytes = phrase.encode()

    # Gerar o hash sha256 da frase
    sha256 = hashlib.sha256(phrase_bytes)

    # Converter o hash em uma representação binária
    bin_sha256 = sha256.digest()

    # Selecionar os primeiros n dígitos
    short_id = bin_sha256[:8]

    # Converter a representação binária de volta para hexadecimal
    hex_short_id = short_id.hex()

    return hex_short_id
```

### Polly para S3
Este script tem como objetivo criar um áudio utilizando a tecnologia Polly da Amazon Web Services (AWS) e armazenar esse áudio no serviço S3 também da AWS.

**Funcionamento**

O script recebe como entrada uma string que será utilizada para criar o áudio. A biblioteca boto3 é utilizada para se conectar à API Polly e criar o áudio, além de armazená-lo no S3.

O arquivo de áudio é salvo com o nome "polly-X.mp3", onde X é o número de arquivos já presentes na pasta do bucket do S3. Além disso, é gerado um link de acesso público ao arquivo armazenado no S3.

O script também retorna um objeto JSON com as informações da frase utilizada para criar o áudio, o link de acesso ao arquivo de áudio e a data e hora em que o arquivo foi criado.

```py
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

    url= s3.generate_presigned_url(
    ClientMethod='get_object',
    Params={
        'Bucket': bucket,
        'Key': 'polly-'+str(len(count))+'.mp3'
    })
    

    brasilia_offset = timedelta(hours=-3)
    brasilia_time = datetime.datetime.utcnow() + brasilia_offset
    formatted_time = brasilia_time.strftime("%Y-%m-%d %H:%M:%S")

    dados = {
        "received_phrase": str(text),
        "url_to_audio": url,
        "created_audio": formatted_time
    }

    return json.dumps(dados)
```
**Uso**

```py
polly_to_s3("Texto a ser transformado em áudio")
```
**Saída**
```json
{
    "received_phrase": "Texto a ser transformado em áudio",
    "url_to_audio": "https://polly-spint6.s3.amazonaws.com/polly-X.mp3",
    "created_audio": "2023-02-13 12:34:56"
}
```

### Upload para o DynamoDB

Uma conexão é feita com o banco de dados utilizando a biblioteca **boto3**, então uma tabela é referenciada, onde os dados do JSON são inseridos.

```py
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
```

### Checagem de ID no DynamoDB

Essencialmente, a [função](https://github.com/Compass-pb-aws-2022-IFCE/sprint-6-pb-aws-ifce/blob/Grupo-5/api-tts/functions/query.py) checa se um determinado item existe em uma tabela do DynamoDB, consultando-o com um identificador. Se o item existir, a função retorna o conteúdo como JSON, se não o valor retornado é *False*.

```py
import json
import boto3

def check_if_item_exists(table_name, unique_id):
    # Criando uma instância do DynamoDB
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
```

## Rotas

**v1/tts**

A [função](https://github.com/Compass-pb-aws-2022-IFCE/sprint-6-pb-aws-ifce/blob/Grupo-5/api-tts/routes/rota1.py) carrega um *body request* em JSON e extrai os valores das chaves *key* e *phrase* de um dicionário.

Se o valor de *key* for o mesmo da chave de segurança predeterminada, então é chamada a função *polly_to_s3()* para armazenar o áudio produzido no S3.

Caso o código hash não seja o mesmo, a condição de erro é acionada retornando o status 500.

```py
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
```

**v2/tts**

Similarmente a rota anterior, essa [função](https://github.com/Compass-pb-aws-2022-IFCE/sprint-6-pb-aws-ifce/blob/Grupo-5/api-tts/routes/rota2.py) lambda converte texto para áudio e salva no S3, com a diferença que a informação do arquivo também é salvo em uma tabela no banco de dados DynamoDB.

Após a checagem da chave de segurança hash, o arquivo vai para o S3 e gera um ID único que é adicionado na resposta da API e é guardado no bando de dados. O resultado do corpo da requisição mostra informações do arquivo de áudio juntamente com o ID gerado.

```py
from functions.hash import generate_short_id
from functions.pollyRequest import polly_to_s3
from functions.upload import insert_json_into_dynamodb

def v2_tts(event, context):
    body = json.loads(event.get('body', '{}'))
    
    # Recuperar os dados enviados na requisição
    key = body.get('key', [])
    data = body.get('phrase', [])
    if key=='749abaa6a1d2a2aa894a5d711b951eb8':
        json_response = polly_to_s3(data)
        json_response = json.loads(json_response)
        json_hash = {"unique_id": generate_short_id(data)}
        json_response.update(json_hash)
        json_response=json.dumps(json_response)
        insert_json_into_dynamodb(json_response,'json_table')
        response = {
                        "statusCode": 200,
                        "body":json_response
                    }
        
        return response
```

**v3/tts**

Essa [rota](https://github.com/Compass-pb-aws-2022-IFCE/sprint-6-pb-aws-ifce/blob/Grupo-5/api-tts/routes/rota3.py) possui características bastante similares a segunda rota, sua função possui como principal diferença a capacidade de checar se o ID ofertado já existe na banco de dados, se esse for o caso o JSON armazenado é retornado, mas se o ID não existir uma novo JSON é gerado e armazenado no **json_table** e retornado para o usuário.

```py
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

    return response
```


## Conclusão

O projeto foi desenvolvido utilizando os serviços da AWS: Polly, S3 e DynamoDB.

Por meio dessas funcionalidades foi possível gerar voz por meio de uma frase e armazenar o áudio gerado, assim como consultar o mesmo. Tudo isso com a utilização da computação em nuvem, que permite aplicações em IA sejam melhoradas de maneira segura, escalável e de fácil gerenciamento.

## Autores
* [Herisson Hyan](https://github.com/herissonhyan)
* [Rangel Pereira](https://github.com/Rangelmello)
* [Luiz Carlos](https://github.com/luiz2CC)
* [Rafael Pereira](https://github.com/Kurokishin)
