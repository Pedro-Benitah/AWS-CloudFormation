# Processamento distribuído de imagens na AWS

Projeto acadêmico que demonstra uma arquitetura produtor-worker-cliente para processamento assíncrono de imagens.

## Arquitetura

1. O cliente envia uma imagem ao produtor por gRPC.
2. O produtor publica a solicitação no RabbitMQ.
3. O worker converte a imagem para escala de cinza com Pillow.
4. O resultado é armazenado em um bucket S3 privado.
5. A infraestrutura é descrita em AWS CloudFormation.

## Tecnologias

- Python 3, gRPC e Protobuf
- RabbitMQ
- AWS EC2 e S3
- AWS CloudFormation
- boto3 e Pillow

## Estrutura

- `cloudformation/template.yaml`: VPC, rede, instâncias, grupos de segurança e bucket S3.
- `app/producer_server.py`: recebe imagens e publica mensagens.
- `app/worker.py`: consome mensagens, processa imagens e grava no S3.
- `app/client.py`: envia imagens ao serviço gRPC.
- `app/image.proto`: contrato gRPC.

## Configuração segura

O repositório não contém endpoints, nomes de bucket nem credenciais reais. Informe os valores do seu próprio ambiente.

No deploy do CloudFormation, restrinja os parâmetros `AllowedClientCidr` e `AllowedSshCidr` aos CIDRs que realmente precisam de acesso. Os valores padrão não abrem os serviços para a internet.

Exemplo de criação da stack:

```bash
aws cloudformation create-stack \
  --stack-name cloudimg-stack \
  --template-body file://cloudformation/template.yaml \
  --parameters \
    ParameterKey=AllowedClientCidr,ParameterValue=SEU_IP_PUBLICO/32 \
    ParameterKey=AllowedSshCidr,ParameterValue=SEU_IP_PUBLICO/32 \
  --capabilities CAPABILITY_IAM
```

Depois do provisionamento, recupere os outputs da stack e configure o ambiente:

```bash
export PRODUCER_GRPC_ADDRESS=HOST_DO_PRODUTOR:50051
export RABBIT_HOST=HOST_PRIVADO_DO_RABBITMQ
export BUCKET_NAME=NOME_DO_BUCKET
python3 app/client.py caminho/para/imagem.jpg
```

As instâncias worker devem usar uma IAM Role com a permissão mínima necessária para gravar no bucket.

## Validação realizada

O fluxo foi validado ponta a ponta em ambiente acadêmico: envio por gRPC, processamento assíncrono, consumo pelo worker e persistência do resultado no S3. O repositório ainda não inclui uma suíte automatizada de testes, métricas de carga ou garantias de produção.

## Segurança e custos

- Use credenciais temporárias e IAM Roles; não grave chaves no código.
- Revise regras de rede antes de cada deploy.
- Remova a stack e os recursos ao terminar o teste para evitar cobranças.
- Se qualquer valor publicado anteriormente ainda estiver ativo, faça a rotação ou substituição no provedor correspondente.
