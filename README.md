
# Sistema Distribuído de Processamento de Imagens em Nuvem

Este projeto implementa um sistema distribuído para processamento de imagens utilizando uma arquitetura baseada em nuvem, comunicação assíncrona e protocolos modernos.

## Arquitetura

- AWS CloudFormation para provisionamento da infraestrutura.
- EC2 para executar produtor, worker e client.
- S3 para armazenamento de imagens processadas.
- RabbitMQ como middleware de mensageria.
- gRPC para comunicação entre o client e o producer.

## Estrutura do Repositório

```
.
├── cloudformation/
│   ├── template.yaml              # Template CloudFormation para provisionamento da infraestrutura
├── app/
│   ├── client.py                   # Cliente gRPC para envio de imagens
│   ├── producer_server.py         # Servidor gRPC que publica imagens na fila RabbitMQ
│   ├── worker.py                  # Worker que consome fila e processa imagens
│   ├── image.proto                # Definição gRPC
│   ├── image_pb2.py, image_pb2_grpc.py # Código gerado pelo protoc
└── README.md                  # Este documento
```

## Código de Infraestrutura

- `template.yaml`: define a VPC, subnets, instâncias EC2, security groups, RabbitMQ container, e bucket S3 com versionamento habilitado.

## Código da Aplicação Distribuída

- Producer (`producer_server.py`): recebe imagens via gRPC e publica na fila `images` do RabbitMQ.
- Worker (`worker.py`): consome imagens da fila, converte para escala de cinza e envia para o bucket S3.
- Client (`client.py`): envia imagens para o producer via gRPC.

## Scripts de Build/Deploy

- Não foi utilizado Docker neste projeto.
- O provisionamento e configuração são feitos via AWS CloudFormation e instalação manual dos componentes na EC2 via `UserData` no template.

## Instruções para Execução Local e em Nuvem

### Provisionamento da Infraestrutura (CloudFormation)

1. Faça o deploy do template:

```bash
aws cloudformation create-stack   --stack-name cloudimg-stack   --template-body file://template.yaml   --capabilities CAPABILITY_IAM
```

2. Aguarde a criação e verifique os outputs:

```bash
aws cloudformation describe-stacks --stack-name cloudimg-stack --query "Stacks[0].Outputs"
```

3. Pegue o IP público da instância Producer para usar no client.

### Configuração e Deploy dos Serviços

#### Producer (EC2 Producer Instance)

O `producer_server.py` já é iniciado manualmente:

```bash
python3 producer_server.py
```

#### Worker (EC2 Worker Instance)

Antes de iniciar o `worker.py`, defina as variáveis de ambiente necessárias:

```bash
export RABBIT_HOST=IP_DO_PRODUTOR
export BUCKET_NAME=NOME_DO_BUCKET_S3
```

Exemplo:

```bash
export RABBIT_HOST=13.220.235.189
export BUCKET_NAME=cloudimg-339713171421-us-east-1-bucket-93b24680
```

Em seguida, execute o worker:

```bash
python3 worker.py
```

Observação: As EC2 workers devem estar associadas a uma IAM Role com permissão S3.

### Testes e Execução

#### Envio de Imagem (Client)

No seu terminal local ou na EC2 Producer:

```bash
python3 client.py CAMINHO-DA-IMAGEM.jpg IP_PRODUCER:50051
```

Exemplo:

```bash
python3 client.py TORTA.jpg 13.220.235.189:50051
```

- O Producer publicará a imagem na fila RabbitMQ.
- O Worker processará e enviará a imagem cinza para o bucket S3.

### Validação

- Acompanhe os logs do `worker.py` para verificar o processamento.
- Verifique no AWS S3 Console se a imagem processada foi enviada corretamente.

## Tecnologias Utilizadas

- AWS EC2, S3, CloudFormation
- RabbitMQ
- Python 3.11
- gRPC + Protobuf
- boto3
- Pillow (PIL)

## Considerações

- Toda a arquitetura segue os requisitos da atividade prática.
- O processamento foi validado end-to-end com múltiplas execuções.
- O uso da IAM Role `LabInstanceProfile` permitiu o acesso seguro ao S3.
# AWS-CloudFormation
