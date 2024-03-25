## como rodar o projeto

### Python dependencias

```BASH

## preciso ter o pip instalado

pip install pika # RabbitMQ
pip install redis
pip install minio

```

### Docker containers

Você precisa rodar o docker conforme abaixo, e usar o min.io com os acessos

MINIO_ROOT_USER: ROOTNAME
MINIO_ROOT_PASSWORD: CHANGEME123

Depois, você precisa gerar um bucket e gerar o access key pela primeira vez no min.io pelo navegador (http://localhost:3000). Feito isso, vá na linha 10, 11 e 12 do arquivo 'fraud-validator-consumer.py' e substitua os campos.

MINIO_ACCESS_KEY = "UHUVRLxqMUV2BUuD9ywB"
MINIO_SECRET_KEY = "F4M8xU71sdj2JmkCZXTap9Tzrktm9WYwJRvTofqD"
MINIO_BUCKET = "relatorio"

```BASH
docker-compose up

docker run --rm -it -p 15672:15672 -p 5672:5672 rabbitmq:3-management

docker run -it --rm --name redis -p 6379:6379 -p 8001:8001 redis/redis-stack:latest

```

### Comandos

```BASH

python3 fraud-validator-consumer.py

python3 transaction-producer.py

```

### Considerações

O Relatório vai ser gerado em TXT após 15 segundos contados a partir da ultima mensagem. A regra de negócio foi definida: Uma transação é considerada fraudulenta se ocorrerem transações em estados diferentes em um curto período de tempo, indicando que não seria fisicamente possível para o cliente viajar entre esses locais tão rapidamente. Os estados são representados por número no relatorio. Se duas transações consecutivas para a mesma conta bancária ocorrem em estados diferentes com menos de 10 minutos de diferença entre elas, é fraude.
