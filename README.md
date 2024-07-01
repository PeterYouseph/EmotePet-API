# Desenvolvimento da aplicação [*'EmotePet API'*]

## 👨‍💻 Projeto desenvolvido por: [Brenno Ostemberg](https://github.com/brenno-ostemberg), [José Pedro Cândido L.P.](https://github.com/PeterYouseph), [Rafael Torres Nantes](https://github.com/rafael-torres-nantes) e [Sarah Baraldi](https://github.com/mbaraldi-sarah).

## Índice

* [📚 Contextualização do projeto](#-contextualização-do-projeto)
* [🛠️ Tecnologias/Ferramentas utilizadas](#%EF%B8%8F-tecnologiasferramentas-utilizadas)
* [🖥️ Funcionamento do sistema](#%EF%B8%8F-funcionamento-do-sistema)
   * [😁 Parte 1 - Emoções](#-parte-1---emoções)
   * [🐶 Parte 2 - Emoções e Pets](#-parte-2---emoções-e-pets)
   * [☁️ Inserindo logs no Cloudwatch](#%EF%B8%8F-inserindo-logs-no-cloudwatch)
   * [🔀 Fluxo da aplicação](#em-resumo-o-fluxo-da-aplicação-se-dá-da-seguinte-forma)
* [📁 Estrutura do projeto](#-estrutura-do-projeto)
* [📌 Como executar o projeto](#-como-executar-o-projeto)
* [🕵️ Dificuldades Encontradas](#%EF%B8%8F-dificuldades-encontradas)

## 📚 Contextualização do projeto

O projeto tem o objetivo de criar uma API que receba imagens postadas no *AWS S3*, utilize o *Amazon Rekognition* identificar bichos e humanos, utilize o *Amazon Bedrock* para extrair dicas de como cuidar dos pets reconhecidos e grave os *logs* dos resultados utilizando *CloudWatch*.


## 🛠️ Tecnologias/Ferramentas utilizadas

[<img src="https://img.shields.io/badge/Visual_Studio_Code-007ACC?logo=visual-studio-code&logoColor=white">](https://code.visualstudio.com/)
[<img src="https://img.shields.io/badge/Git-232F3E?logo=git&logoColor=red">](https://git-scm.com/)
[<img src="https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=violet">](https://github.com/)
[<img src="https://img.shields.io/badge/AWS-fda100?logo=amazon-aws&logoColor=white">](https://aws.amazon.com/pt/)
[<img src="https://img.shields.io/badge/AWS-CLI-232F3E?logo=amazon-aws&logoColor=white">](https://aws.amazon.com/pt/cli/)
[<img src="https://img.shields.io/badge/AWS-S3-dd2304?logo=amazon-aws&logoColor=white">](https://aws.amazon.com/pt/s3/)
[<img src="https://img.shields.io/badge/AWS-Cloudwatch-green?logo=amazon-aws&logoColor=white">](https://aws.amazon.com/pt/cloudwatch/)
[<img src="https://img.shields.io/badge/Amazon-Bedrock-01ac71?logo=amazon-aws&logoColor=white">](https://aws.amazon.com/pt/bedrock/)
[<img src="https://img.shields.io/badge/Amazon-Rekognition-blue?logo=amazon-aws&logoColor=white">](https://aws.amazon.com/pt/rekognition/)
[<img src="https://img.shields.io/badge/Serverless_Framework-ff5242?logo=amazon-aws&logoColor=white">](https://www.serverless.com)

#### Organização do Time:

[<img src="https://img.shields.io/badge/Trello-0079BF?logo=trello&logoColor=white">](https://trello.com/)
[<img src="https://img.shields.io/badge/Teams-6264A7?logo=microsoft-teams&logoColor=white">](https://www.microsoft.com/pt-br/microsoft-teams/group-chat-software)

## 🖥️ Funcionamento do sistema

### 😁 Parte 1 - Emoções

Utilizando o *framework* **Serverless**, enviamos um *json* via **POST** à rota `/v1/vision`, onde utilizamos o **Amazon Rekognition** para detectar as faces e emoções. Além disso, são efetuados *logs* referentes a cada solitação no **AWS Cloudwatch**.

#### Exemplo de entrada:

<!-- Terminar -->
```json 
{ 
   "bucket": "nomeBucket", 
   "imageName": "nomeFoto.jpg" 
} 
```

#### Exemplos de Saída:

1. Caso haja apenas uma face:

<!-- Terminar -->
```json 
{ 
   "url_to_image": "https://myphotos/test.jpg", 
   "created_image": "02-02-2023 17:00:00", 
   "faces": [ 
     { 
      "position": 
      { 
       "Height": 0.06333330273628235, 
       "Left": 0.1718519926071167, 
       "Top": 0.7366669774055481, 
       "Width": 0.11061699688434601 
      } 
      "classified_emotion": "HAPPY", 
      "classified_emotion_confidence": 99.92965151369571686 
     } 
   ] 
} 
```

2. Caso haja mais de uma face, o elemento *"faces": [{...}]* recebe mais de um objeto:

<!-- Terminar -->
```json
"faces": [ 
     { 
      "position": 
      { 
       "Height": 0.06333330273628235, 
       "Left": 0.1718519926071167, 
       "Top": 0.7366669774055481, 
       "Width": 0.11061699688434601 
      } 
      "classified_emotion": "HAPPY", 
      "classified_emotion_confidence": 99.92965151369571686 
     },
     { 
      "position": 
      { 
       "Height": 0.08333330273628235, 
       "Left": 0.3718519926071167, 
       "Top": 0.6366669774055481, 
       "Width": 0.21061699688434601 
      } 
      "classified_emotion": "HAPPY", 
      "classified_emotion_confidence": 98.92965151369571686 
     }
   ]
```

3. Caso **NÃO** haja faces, os elementos contidos em *"faces": [{...}]* recebem valor *NULL*:

<!-- Terminar -->
```json 
{ 
   "url_to_image": "https://myphotos/test.jpg", 
   "created_image": "02-02-2023 17:00:00", 
   "faces": [ 
     { 
      "position": 
      { 
       "Height": Null, 
       "Left": Null, 
       "Top": Null, 
       "Width": Null 
      } 
      "classified_emotion": Null, 
      "classified_emotion_confidence": Null 
     } 
] 
} 
``` 

#### Detectando elementos:

- **Detectando as *faces***: utilizamos a função `detect_faces` da seguinte forma:

```py
response = self.rekognition.detect_faces(
   Image={
      'S3Object': {
         'Bucket': bucket,
         'Name': image_name
      }
   },
   Attributes=['ALL']
)
```

- **Detectando as *emoções***: utilizamos a função `detect_labels` da seguinte forma:

```py
response = self.rekognition.detect_labels(
   Image={
      'S3Object': {
         'Bucket': bucket,
         'Name': image_name
      }
   },
   MaxLabels=10,
   MinConfidence=80
)
```

### 🐶 Parte 2 - Emoções e Pets

De maneira análoga à Parte 1, desenvolvemos o sistema utilizamos o *framework* **Serverless** para enviarmos um *json* via **POST** à rota `/v2/vision`, onde utilizamos o **Amazon Rekognition** para detectar os pets, suas emoções e raças. Além disso, utilizamos o **Amazon Bedrock** para receber **dicas** de cuidados para cada raça dos pets reconhecidos. Por fim, são efetuados *logs* referentes a cada solitação no **AWS Cloudwatch**.

#### Exemplo de entrada:

<!-- Terminar -->
```json 
{ 
   "bucket": "nomeBucket", 
   "imageName": "nomeFoto.jpg" 
} 
```

#### Exemplos de Saída:

<!-- Terminar -->
1. Caso haja **apenas um pet**:

```json 
{  
   "url_to_image": "https://mycatphotos/cat.jpg",  
   "created_image": "02-02-2023 17:00:00",  
   "pets": [
      {
      "labels": [  
      {  
         "Confidence": 96.59198760986328,  
         "Name": "Animal"  
      },  
      {  
         "Confidence": 96.59198760986328,  
         "Name": "Dog"  
      },  
      {  
         "Confidence": 96.59198760986328,  
         "Name": "Pet"  
      },  
      {  
         "Confidence": 96.59198760986328,  
         "Name": "Labrador"  
      }  
      ]  
      "Dicas:": " 
      Dicas sobre Labradores: 
      Nível de Energia e Necessidades de Exercícios: Labradores são de médio nível de energia, necessitando de 40 minutos de exercício por dia. 
      Temperamento e Comportamento: Inteligentes, enérgicos, dóceis, e com forte desejo de trabalhar com pessoas. 
      Cuidados e Necessidades: Pelos curtos que precisam de poucos cuidados, mas devem ser penteados uma vez por semana para remover fios mortos e soltos. A alimentação deve ser adequada, ajustando a quantidade conforme o peso do cão. 
      Problemas de Saúde Comuns: Displasia do cotovelo e coxofemoral, atrofia progressiva da retina (APR) e catarata hereditária. 
      " 
      }
   ]
} 
```

2. Caso haja **uma pessoa e um pet**, retorna uma resposta como à da Parte 1, e também informações de pet, como no exemplo anterior:

<!-- Terminar -->
```json
{ 
   "url_to_image": "https://myphotos/test.jpg", 
   "created_image": "02-02-2023 17:00:00", 
   "faces": [ 
     { 
      "position": 
      { 
       "Height": 0.06333330273628235, 
       "Left": 0.1718519926071167, 
       "Top": 0.7366669774055481, 
       "Width": 0.11061699688434601 
      } 
      "classified_emotion": "HAPPY", 
      "classified_emotion_confidence": 99.92965151369571686 
     } 
   ],
   "pets": [
      {
      "labels": [  
      {  
         "Confidence": 96.59198760986328,  
         "Name": "Animal"  
      },  
      {  
         "Confidence": 96.59198760986328,  
         "Name": "Dog"  
      },  
      {  
         "Confidence": 96.59198760986328,  
         "Name": "Pet"  
      },  
      {  
         "Confidence": 96.59198760986328,  
         "Name": "Labrador"  
      }  
      ]  
      "Dicas:": " 
      Dicas sobre Labradores: 
      Nível de Energia e Necessidades de Exercícios: Labradores são de médio nível de energia, necessitando de 40 minutos de exercício por dia. 
      Temperamento e Comportamento: Inteligentes, enérgicos, dóceis, e com forte desejo de trabalhar com pessoas. 
      Cuidados e Necessidades: Pelos curtos que precisam de poucos cuidados, mas devem ser penteados uma vez por semana para remover fios mortos e soltos. A alimentação deve ser adequada, ajustando a quantidade conforme o peso do cão. 
      Problemas de Saúde Comuns: Displasia do cotovelo e coxofemoral, atrofia progressiva da retina (APR) e catarata hereditária. 
      " 
      }
   ]
}
```

#### Detectando elementos:

- **Detectando os *pets***: utilizamos a função `detect_labels`:

```py
def detect_pets(self, bucket, image_name):
   labels_response = self.detect_labels(bucket, image_name)
   animal_characteristics = self.animal_characteristics(labels_response)
   pets = self.pets_labels_treatment(animal_characteristics)
   return pets
```

- Filtramos a resposta da função para obtermos os **pets**:

```py
def animal_characteristics(self, rekognition_response):
   # Lista de rótulos de possíveis animais de estimação
   pet_labels = ['Dog', 'Cat', 'Bird', 'Fish', 'Reptile', 'Mammal', 'Pet']
   animal_characteristics = []
   for label in rekognition_response["Labels"]:
      for parent in label["Parents"]:
            if parent.get("Name") in pet_labels:
               animal_characteristics.append(label)
   return animal_characteristics
```

- Para obtermos mais **precisão** no reconhecimento das raças dos animais, filtramos "raças genéricas" do elemento ***breed***.

```py
def _process_pets(self, pet_labels):
   pets = []
   filtered_breeds = ['Animal', 'Pet', 'Dog', 'Bird', 'Mammal', 'Vertebrate', 'Canidae','Canine', 'Carnivore', 'Terrestrial animal', 'Dog breed', 'Dog like mammal']
   unique_breeds = {breed['Name']: breed for pet in pet_labels["pets"] for breed in pet["labels"] if breed['Name'] not in filtered_breeds}.values()

   # Gera o log das raças únicas detectadas pelo Rekognition
   logger(f'Raças únicas: {unique_breeds}')

   # Para cada raça de animal de estimação detectada pelo Rekognition
   for breed in unique_breeds:
      self.bedrock_service.set_pet_breed(breed['Name'])
      response = self.bedrock_service.invoke_model()
      if response['statusCode'] == 200:
            tips = json.loads(response['Dicas'])
      else:
            tips = 'Erro ao obter dicas do Bedrock'

      pet_info = {
            'labels': [{'Confidence': breed['Confidence'], 'Name': breed['Name']}],
            'Dicas': tips
      }
      pets.append(pet_info)

   return pets
```

### ☁️ Inserindo logs no Cloudwatch

Tanto na Parte 1 quanto na Parte 2, inserimos *logs* no **Cloudwatch**. Os *logs* foram formatados da seguinte maneira:

```py
log_event = {
   'logGroupName': log_group_name,
   'logStreamName': log_stream_name,
   'logEvents': [
      {
         'timestamp': int(datetime.datetime.now().timestamp() * 1000),
         'message': json.dumps(message)
      }
   ]
}
```

Criamos duas classificações de *logs*.

1. Quando a requisição for um sucesso:

```py
def logger(message):
    print(message)
    logger_instance.log_message('rekognition-logs', 'vision-logs', message)
```

2. Quando houver algum erro:

```py
def error(message):
    print(message)
    logger_instance.log_message('rekognition-logs', 'vision-errors', message)
```

### Em resumo, o fluxo da aplicação se dá da seguinte forma:

![Fluxo da Aplicação](./assets/arquitetura-base.jpg)

## 📁 Estrutura do projeto 

#### O projeto foi dividido nos seguintes diretórios, baseando-se no modelo MVC (Model-View-Controller) com devidas adaptações:

#### Divisão dos diretórios:

- `controller` → Realiza a chamada dos *services* (em ./services) criados para gerenciar os serviços AWS, sendo *bucket* na **S3**, reconhecimento no **Amazon Rekognition** e criação de texto no **Amazon Bedrock**.

- `services` → Manipulam os serviços AWS obtendo os **metadados** e gera **URL** das imagens no **S3**, detecta faces e rótulos no **Amazon Rekognition**, cria prompt e obtem respostas no **Amazon Bedrock**.

- `utils` → Manipula os ***logs*** no **Cloudwatch** e faz *upload* de imagens no **S3**.

#### Outros arquivos importantes:

- `handler.py` → Contém as funções que sintetizam a API e define suas rotas. Verifica a saúde da API, recebe a imagem do **S3** e retorna os detalhes do reconhecimento do **Amazon Rekognition**.

- `serverless.yml` → Define as políticas **IAM** para permitir que as **funções Lambda** acessem os serviços necessários e rotas das requisições que serão usadas no *handler.py*. 

## 📌 Como executar o projeto

### Clone o repositório

```bash
$ git clone https://github.com/Compass-pb-aws-2024-MARCO/sprint-8-pb-aws-marco.git 
```

### Acesse a pasta do projeto no terminal/cmd:

```bash
$ cd sprints-8-pb-aws-marco
```

### Realize um check-out para a branch de desenvolvimento:

```bash
$ git checkout grupo-2
```

### Cerfitique-se ue tem o serverless instalado:

```bash
$ serverless
```

### Caso não estiver, instale poe meio do comando:

```bash
$ npm install -g serverless
```

### Instale os plugins do serverless:

```bash
$ npm install serverless-python-requirements serverless-dotenv-plugin
```

### Configure as credenciais da aws:

```bash
$ aws configure
```

### Faça login no serverless:

```bash
$ serverless login
```

### Acesse a pasta visao-computacional:

```bash
$ cd visao-computacional
```

### Execute o seguinte comando para realizar o deploy:
```bash
$ serverless deploy
```

<!-- Terminar -->

## 🕵️ Dificuldades Encontradas

### ⚙ Dificuldades Técnicas

O Rekognition retorna diversos dados, incluindo informações que **não eram necessárias** para nosso uso, referidas como "raças genéricas". Conseguimos solucionar o problema [aplicando filtros](#detectando-elementos-1) aos dados. No entanto, essa solução só foi alcançada após a análise de vários exemplos de retorno e uma **extensa** pesquisa na documentação do Rekognition sobre o tópico, especialmente na [API Vision V2 (Emoções + Pets)](#parte-2---emoções-e-pets).

Outra dificuldade que enfrentamos foi o **timeout** ao configurarmos o *Bedrock*. O API Gateway possui um limite de 30 segundos para requisições HTTP, enquanto o *Bedrock* levava quase **5 minutos** para retornar os dados, mesmo para apenas um pet. Resolvemos esse problema realizando algumas modificações no código, ajustando os atributos **maxTokenCount**, **temperature** e **topP** no arquivo `bedrock_services.py`.

```py
def generate_request_body(self):
   request_body = {
      "inputText": self.create_prompt(),
      "textGenerationConfig": {
            "maxTokenCount": 128,
            # temperature:  aleatoriedade na geração de texto
            "temperature": 0.7,
            # topP:  tokens que compõem o top p% da probabilidade cumulativa
            "topP": 0.9
      },
   }
   return json.dumps(request_body)
```

### 📝 Dificuldades de Organização

<!-- ... -->
