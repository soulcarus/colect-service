package main

import (
	"context"
	"log/slog"
	"os"
	"os/signal"
	"syscall"
	"time"

	"colect-service/internal/collector"
	"colect-service/internal/config"
	"colect-service/internal/logging"
	"colect-service/internal/opcua"
	"colect-service/internal/storage"
)

func main() {
	logWriter, err := logging.NewDailyWriter("logs")
	if err != nil {
		slog.Error("Falha crítica na configuração do logger", "err", err)
		os.Exit(1)
	}
	defer logWriter.Close()

	fileHandler := slog.NewTextHandler(logWriter, &slog.HandlerOptions{Level: slog.LevelDebug})
	consoleHandler := slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo})

	logger := slog.New(fileHandler)
	loggerConsole := slog.New(consoleHandler)

	slog.SetDefault(logger)

	slog.Info("Iniciando aplicação")
	loggerConsole.Info("Iniciando aplicação (console)")
	defer slog.Info("Aplicação finalizada")

	cfg, err := config.Load("config/opcua.yaml")
	if err != nil {
		slog.Error("Falha crítica na configuração", "err", err)
		loggerConsole.Error("Falha crítica na configuração", "err", err)
		os.Exit(1)
	}

	opcuaClient, err := opcua.NewClient(cfg.OPCUA)
	if err != nil {
		slog.Error("Falha ao criar cliente OPC-UA", "err", err)
		loggerConsole.Error("Falha ao criar cliente OPC-UA", "err", err)
		os.Exit(1)
	}

	ctxConnect, cancelConnect := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancelConnect()
	if err := opcuaClient.Connect(ctxConnect); err != nil {
		slog.Error("Falha ao conectar no servidor OPC-UA", "err", err)
		loggerConsole.Error("Falha ao conectar no servidor OPC-UA", "err", err)
		os.Exit(1)
	}
	defer opcuaClient.Disconnect()

	mongoDB := storage.NewMongoDB(cfg.MongoDB.URI)
	defer mongoDB.Disconnect()

	collectorSvc := collector.NewService(opcuaClient, mongoDB, cfg)
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		slog.Info("Iniciando coletor...")
		loggerConsole.Info("Iniciando coletor...")
		collectorSvc.Start(ctx)
	}()

	<-stop
	slog.Info("Recebido sinal de desligamento...")
	loggerConsole.Info("Recebido sinal de desligamento...")
	cancel()
	time.Sleep(1 * time.Second)
	slog.Info("Serviço encerrado")
	loggerConsole.Info("Serviço encerrado")
}
