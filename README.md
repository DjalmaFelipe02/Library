# Biblioteca

## Descrição

A Biblioteca é um sistema de gerenciamento de livros que permite aos usuários realizar operações como cadastro, consulta, empréstimo e devolução de livros. Ele oferece recursos avançados, como filtro de pesquisa por categoria e estado de empréstimo, controle de datas de devolução e muito mais.


## Instalação

1. Clone o repositório para sua máquina local:
``` 
git clone https://github.com/DjalmaFelipe02/Library.git
```
2. Navegue até o diretório do projeto:
``` 
cd code
```
3. Inicialize um ambiente virtual:
``` 
py -m venv venv
```
4. Ative o ambiente virtual (comando para Windows):
``` 
venv\Scripts\activate
```
5. Instale as dependências do projeto:
``` 
pip install -r requirements.txt
```
6. Execute as migrações do Django para criar o esquema do banco de dados:
``` 
python manage.py makemigrations
python manage.py migrate
```
## Uso

Para executar o servidor de desenvolvimento, execute o seguinte comando:
``` 
python manage.py runserver
```
Isso iniciará o servidor de desenvolvimento em 'http://localhost:8000/'.

Depois coloque essa URL 'http://localhost:8000/index' para acessar a página.
