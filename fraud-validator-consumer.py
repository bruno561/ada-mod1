import json
import pika
import threading
import redis
from datetime import datetime, timedelta
from minio import Minio
from minio.error import S3Error

# Configurações
MINIO_ACCESS_KEY = {{secret.MINIO_ACCESS_KEY}}
MINIO_SECRET_KEY = {{secret.MINIO_SECRET_KEY}}
MINIO_BUCKET = "relatorio"
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672

# Inicializações
minio_client = Minio("localhost:9000", access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
transacoes = []

# Temporizador para a geração automática do relatório
temporizador = None

def gerar_e_enviar_relatorio():
    global transacoes
    if not transacoes:
        print("Nenhuma transação recebida para gerar relatório.")
        return

    print("Iniciando a geração do relatório...")
    relatorio_content = "\n".join(
        [f"Transacao ID: {t['id']}, Conta: {t['account_number']}, Estado: {t['estado']}, Valor: {t['value']}, Data: {t['data']}" 
         for t in transacoes])
    relatorio_content += "\nExistem transações suspeitas." if any(t.get('suspeita', False) for t in transacoes) else "\nNão existem transações suspeitas."
    
    arquivo_relatorio = "relatorio_transacoes.txt"
    with open(arquivo_relatorio, 'w') as f:
        f.write(relatorio_content)
    
    try:
        # Upload do relatório para o MinIO
        minio_client.fput_object(MINIO_BUCKET, arquivo_relatorio, arquivo_relatorio)
        # Gera o URL pré-assinado para o relatório
        url = minio_client.presigned_get_object(MINIO_BUCKET, arquivo_relatorio, expires=timedelta(days=1))
        print(f"Relatório enviado para o MinIO com sucesso. URL: {url}")

        # Grava o URL em um arquivo e faz upload para o MinIO
        arquivo_url = "url_relatorio.txt"
        with open(arquivo_url, 'w') as f_url:
            f_url.write(url)
        minio_client.fput_object(MINIO_BUCKET, arquivo_url, arquivo_url)
        
    except S3Error as e:
        print(f"Erro ao enviar o relatório ou URL para o MinIO: {e}")

    # Limpa a lista de transações após o relatório ser gerado e enviado
    transacoes.clear()

def iniciar_temporizador():
    global temporizador
    # Reinicia o temporizador
    if temporizador is not None:
        temporizador.cancel()
    temporizador = threading.Timer(15.0, gerar_e_enviar_relatorio)
    temporizador.start()


def processar_transacao(channel, method, properties, body):
    global transacoes
    transacao = json.loads(body)
    print(f"Transação recebida: {transacao}")
    transacoes.append(transacao)
    # Reinicia o temporizador a cada nova mensagem recebida
    iniciar_temporizador()


def main():
    # Estabelece conexão com o RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, virtual_host="/"))
    channel = connection.channel()

    # Configuração da fila e início do consumo de mensagens
    queue_name = "fraud_validator_queue"
    channel.queue_declare(queue=queue_name)
    channel.queue_bind(exchange='amq.fanout', queue=queue_name)
    
    channel.basic_consume(queue=queue_name, on_message_callback=processar_transacao, auto_ack=True)
    
    print("Esperando por mensagens. Para sair pressione CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Processo interrompido pelo usuário.")
    finally:
        if connection.is_open:
            connection.close()
            

if __name__ == "__main__":
    main()
