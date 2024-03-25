import datetime
import pika
import json
import time
import random

def conectar_a_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", port=5672, virtual_host="/"))
    channel = connection.channel()
    return connection, channel

def publicar_mensagens(channel, transactions):
    properties = pika.BasicProperties(app_id="transaction-producer.py", content_type="application/json")

    for transaction in transactions:
        # Atualizando os campos com valores inteiros aleatórios
        transaction["account_number"] = random.randint(1, 10000)
        transaction["estado"] = random.randint(1, 27)

        transaction["data"] = datetime.datetime.utcnow().isoformat() + 'Z'

        channel.basic_publish(
            exchange="amq.fanout",
            routing_key="",
            body=json.dumps(transaction),
            properties=properties,
        )
        print(f"[x] Sent '{json.dumps(transaction)}'")
        time.sleep(5)

def carregar_transacoes_do_arquivo(nome_do_arquivo):
    with open(nome_do_arquivo) as transaction_file:
        transactions = json.load(transaction_file)
    return transactions

def main():
    connection, channel = conectar_a_rabbitmq()
    transactions = carregar_transacoes_do_arquivo("transaction.json")
    publicar_mensagens(channel, transactions)
    channel.close()
    connection.close()

if __name__ == "__main__":
    main()
