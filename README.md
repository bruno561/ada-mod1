# Mensageiria

## RabbitMQ

### Docker

```BASH
docker run --rm -it -p 15672:15672 -p 5672:5672 rabbitmq:3-management
```

Depois que o comando acima tiver sido executado, você poderá acessar o portal do RabbitMQ em http://localhost:15672/

Usuário: `guest`
Senha: `guest`

### CLI

[rabbitmqadmin](http://localhost:15672/cli/rabbitmqadmin)

```BASH
sudo curl -o /usr/local/bin/rabbitmqadmin http://localhost:15672/cli/rabbitmqadmin
```
