# shapefiles-brasil

Script que coleta shapefiles do IBGE, converte para GeoJSON e gera versões simplificadas (menos pontos e menor
tamanho).

Em breve os dados estarão disponíveis para download no [Brasil.IO](https://brasil.io/).


## Instalando

Necessita de Python (testado em 3.13 - algumas dependências podem não funcionar em versões mais recentes). Instale as
bibliotecas rodando:

```shell
pip install -r requirements.txt
```


## Rodando

```shell
./run.sh
```

Caso prefira rodar dentro de um container Docker, execute `make build` para criar a imagem e `make bash` para abrir o
shell dentro do container. Para ver as opções disponíveis, execute `make help`.
