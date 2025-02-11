package storage

import (
	"context"
	"log/slog"
	"time"

	"colect-service/internal/models"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type MongoDB struct {
	client *mongo.Client
	db     *mongo.Database
}

func NewMongoDB(uri string) *MongoDB {
	slog.Info("Conectando ao MongoDB", "uri", uri)

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	client, err := mongo.Connect(ctx, options.Client().ApplyURI(uri))
	if err != nil {
		slog.Error("Conexão falhou", "err", err)
		panic(err)
	}

	if err = client.Ping(ctx, nil); err != nil {
		slog.Error("Ping falhou - conexão inativa", "err", err)
		panic(err)
	}

	slog.Info("Conexão com MongoDB estabelecida com sucesso")
	return &MongoDB{
		client: client,
		db:     client.Database("colect-service"),
	}
}

func (m *MongoDB) InsertCycle(ctx context.Context, cycle models.Cycle) error {
	collection := m.db.Collection("cycles")
	_, err := collection.InsertOne(ctx, cycle)
	return err
}

func (m *MongoDB) Disconnect() {
	if err := m.client.Disconnect(context.Background()); err != nil {
		slog.Error("Erro ao desconectar do MongoDB", "err", err)
	}
}
