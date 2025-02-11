mt08-collector/
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