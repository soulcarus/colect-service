# Colect Service

## Visão Geral

O **Colect Service** é um serviço de coleta de dados via protocolo OPC-UA, projetado para capturar variáveis de sensores industriais e armazená-las no MongoDB. Ele é implementado em Go e possui uma arquitetura modular para facilitar a escalabilidade e manutenção.

## Estrutura do Projeto

```
colect-service/
├── cmd/
│   └── collector/
│       └── main.go           # Ponto de entrada e graceful shutdown
├── internal/
│   ├── opcua/                # Cliente OPC-UA
│   │   ├── client.go         # Conexão e leitura de tags
│   │   └── config.go         # Configurações fixas (URL, tags)
│   ├── collector/            # Lógica de coleta cíclica
│   │   ├── service.go        # Gerenciamento de ciclos e buffer
│   │   └── processor.go      # Processamento e inserção no MongoDB
│   └── storage/
│       └── mongodb.go        # Operações de inserção em batch
├── config/
│   └── opcua.yaml            # Configurações do OPC-UA e MongoDB
├── go.mod
└── Dockerfile
```

## Configuração

Antes de executar o serviço, verifique e edite as configurações no arquivo `config/opcua.yaml`. Nele, você deve definir:

- **Endereço do servidor OPC-UA**
- **Tags a serem coletadas**
- **Configuração do MongoDB**

## Como Executar

### Localmente

1. **Instale as dependências:**
   ```sh
   go mod tidy
   ```
2. **Inicie o serviço:**
   ```sh
   go run ./cmd/collector . 
   ```

### Via Docker

1. **Construa a imagem Docker:**
   ```sh
   docker build -t colect-service . 
   ```
2. **Execute o container:**
   ```sh
   docker run --rm -d --name collector colect-service
   ```

## Gerar Relatório

O serviço gera logs de coleta, que podem ser usados para criar um relatório em PDF.

Para gerar um relatório, execute:

```sh
python3 gerar_relatorio.py logs/2025-02-09.log --output relatorio.pdf
```

Isso irá processar o log especificado e gerar um arquivo PDF com as estatísticas da coleta.
