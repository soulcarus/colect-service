package collector

import (
	"context"
	"log/slog"
	"time"

	"colect-service/internal/config"
	"colect-service/internal/models"
	"colect-service/internal/opcua"
	"colect-service/internal/storage"
)

type Service struct {
	opcuaClient *opcua.Client
	storage     *storage.MongoDB
	cfg         *config.Config
}

func NewService(opcuaClient *opcua.Client, storage *storage.MongoDB, cfg *config.Config) *Service {
	return &Service{
		opcuaClient: opcuaClient,
		storage:     storage,
		cfg:         cfg,
	}
}

func (s *Service) Start(ctx context.Context) {
	interval := s.cfg.Collector.CycleDuration / time.Duration(s.cfg.Collector.SamplesPerCycle)

	slog.Info("Iniciando coleta cíclica",
		"duracao_ciclo", s.cfg.Collector.CycleDuration,
		"amostras_por_ciclo", s.cfg.Collector.SamplesPerCycle,
		"intervalo_amostragem", interval)

	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			slog.Info("Coletor encerrado")
			return

		default:
			cycle := models.Cycle{
				StartTime: time.Now().UTC(),
				Samples:   make([]models.Sample, 0, s.cfg.Collector.SamplesPerCycle),
			}

			// Coleta as amostras do ciclo
			for i := 0; i < s.cfg.Collector.SamplesPerCycle; i++ {
				select {
				case <-ticker.C:
					values, err := s.opcuaClient.Read(ctx)
					if err != nil {
						slog.Error("Erro na leitura", "err", err)
						continue
					}

					cycle.Samples = append(cycle.Samples, models.Sample{
						Timestamp: time.Now().UTC(),
						Values:    values,
					})

				case <-ctx.Done():
					slog.Warn("Ciclo interrompido", "amostras_coletadas", len(cycle.Samples))
					return
				}
			}

			// Finaliza e salva o ciclo
			cycle.EndTime = time.Now().UTC()
			if err := s.storage.InsertCycle(ctx, cycle); err != nil {
				slog.Error("Erro ao salvar ciclo", "err", err)
			} else {
				slog.Info("Ciclo salvo",
					"amostras", len(cycle.Samples),
					"duracao_real", cycle.EndTime.Sub(cycle.StartTime))
			}
		}
	}
}
