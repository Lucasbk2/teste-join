# teste-join

##Instalação

### Criar nova venv

Criar venv

python -m venv venv

Ativar a venv/configurar venv na IDE

### Instalar requirements

Instalar requirements encontrado e testejoin/requirements.txt

pip install -r requirements.txt

### Configurar váriveis de ambiente
No caminho >
_testejoin/testejoin/.env_
inserir varíaveis de ambiente.

PostgresDatabaseName=Nome do Schema

PostgresUsername= Username do Administrador

PostgresPass= Senha do Administrador

PostgresHost= Host Local Ex: localhost

PostgresPort= Porta Ex: 5432

### Executar as migrações

Executar os comandos em _testejoin/testejoin/_

python manage.py makemigrations

python manage.py migrate

### Executar o programa

Executar em _testejoin/testejoin/_

python manage.py runserver