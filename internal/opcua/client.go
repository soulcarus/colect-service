package opcua

import (
	"context"
	"fmt"
	"log/slog"

	"github.com/gopcua/opcua"
	"github.com/gopcua/opcua/ua"
)

type Client struct {
	client  *opcua.Client
	nodeIDs []*ua.NodeID
}

func (c *Client) NodeIDs() []*ua.NodeID {
	return c.nodeIDs
}

type Config struct {
	ServerURL string   `mapstructure:"server_url"` // Alterado de yaml para mapstructure
	Tags      []string `mapstructure:"tags"`       // Alterado de yaml para mapstructure
}

func NewClient(cfg Config) (*Client, error) {
	nodeIDs := make([]*ua.NodeID, len(cfg.Tags))
	for i, tag := range cfg.Tags {
		nodeIDs[i] = ua.MustParseNodeID(tag)
	}

	fmt.Println(cfg.ServerURL)

	endpoints, err := opcua.GetEndpoints(context.Background(), cfg.ServerURL)
	if err != nil {
		return nil, fmt.Errorf("falha ao obter endpoints: %w", err)
	}

	ep, err := opcua.SelectEndpoint(
		endpoints,
		ua.SecurityPolicyURINone,
		ua.MessageSecurityModeNone,
	)
	if err != nil {
		return nil, fmt.Errorf("seleção de endpoint falhou: %w", err)
	}

	opts := []opcua.Option{
		opcua.SecurityPolicy(ua.SecurityPolicyURINone),
		opcua.SecurityMode(ua.MessageSecurityModeNone),
	}

	cli, err := opcua.NewClient(ep.EndpointURL, opts...)
	if err != nil {
		return nil, fmt.Errorf("criação do cliente falhou: %w", err)
	}

	return &Client{
		client:  cli,
		nodeIDs: nodeIDs,
	}, nil
}

func (c *Client) Connect(ctx context.Context) error {
	return c.client.Connect(ctx)
}

func (c *Client) Read(ctx context.Context) (map[string]float64, error) {
	slog.Info("Iniciando leitura de tags OPC-UA", "total_tags", len(c.nodeIDs))

	req := &ua.ReadRequest{
		NodesToRead: make([]*ua.ReadValueID, len(c.nodeIDs)),
	}
	for i, nodeID := range c.nodeIDs {
		req.NodesToRead[i] = &ua.ReadValueID{NodeID: nodeID}
	}

	resp, err := c.client.Read(ctx, req)
	if err != nil {
		slog.Error("Falha na requisição de leitura OPC-UA", "err", err)
		return nil, fmt.Errorf("leitura falhou: %w", err)
	}

	values := make(map[string]float64)
	for i, result := range resp.Results {
		tag := c.nodeIDs[i].String()
		if result.Status != ua.StatusOK {
			slog.Warn("Tag com status inválido",
				"tag", tag,
				"status", result.Status)
			continue
		}
		val := convertValue(result.Value.Value())
		slog.Debug("Tag lida com sucesso",
			"tag", tag,
			"valor", val,
			"tipo", fmt.Sprintf("%T", result.Value.Value()))
		values[tag] = val
	}

	slog.Info("Leitura OPC-UA concluída",
		"tags_lidas", len(values),
		"tags_falhas", len(c.nodeIDs)-len(values))
	return values, nil
}

func convertValue(v interface{}) float64 {
	switch val := v.(type) {
	case float64:
		return val
	case float32:
		return float64(val)
	case int, int8, int16, int32, int64:
		return float64(val.(int64))
	case uint, uint8, uint16, uint32, uint64:
		return float64(val.(uint64))
	case bool:
		if val {
			return 1
		}
		return 0
	default:
		return 0
	}
}

func (c *Client) Disconnect() {
	c.client.Close(context.Background())
}
