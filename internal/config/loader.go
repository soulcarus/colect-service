package config

import (
	"colect-service/internal/opcua"
	"fmt"
	"time"

	"github.com/spf13/viper"
)

type Config struct {
	OPCUA     opcua.Config `mapstructure:"opcua"`
	Collector struct {
		CycleDuration   time.Duration `mapstructure:"cycle_duration"`
		SamplesPerCycle int           `mapstructure:"samples_per_cycle"`
	} `mapstructure:"collector"`
	MongoDB struct {
		URI string `mapstructure:"uri"`
	} `mapstructure:"mongodb"`
}

func Load(path string) (*Config, error) {
	viper.SetConfigFile(path)
	if err := viper.ReadInConfig(); err != nil {
		return nil, fmt.Errorf("erro ao ler arquivo: %w", err) // Mais detalhes
	}

	var cfg Config
	if err := viper.Unmarshal(&cfg); err != nil {
		return nil, fmt.Errorf("erro ao decodificar config: %w", err)
	}

	// Log temporário para verificar valores
	fmt.Printf("Configuração carregada:\n%+v\n", cfg)

	return &cfg, nil
}
