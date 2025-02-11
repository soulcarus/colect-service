package logging

import (
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"
)

type DailyWriter struct {
	baseDir     string
	currentDate string
	file        *os.File
	mu          sync.Mutex
}

func NewDailyWriter(baseDir string) (*DailyWriter, error) {
	if err := os.MkdirAll(baseDir, 0755); err != nil {
		return nil, fmt.Errorf("erro ao criar diretório de logs: %w", err)
	}

	w := &DailyWriter{
		baseDir: baseDir,
	}

	if err := w.rotate(); err != nil {
		return nil, err
	}

	return w, nil
}

func (w *DailyWriter) Write(p []byte) (n int, err error) {
	w.mu.Lock()
	defer w.mu.Unlock()

	currentDate := time.Now().Format("2006-01-02")
	if currentDate != w.currentDate {
		if err := w.rotate(); err != nil {
			return 0, fmt.Errorf("erro na rotação do log: %w", err)
		}
	}

	return w.file.Write(p)
}

func (w *DailyWriter) rotate() error {
	if w.file != nil {
		w.file.Close()
	}

	w.currentDate = time.Now().Format("2006-01-02")
	filePath := filepath.Join(w.baseDir, w.currentDate+".log")

	file, err := os.OpenFile(filePath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return fmt.Errorf("erro ao abrir arquivo de log: %w", err)
	}

	w.file = file
	return nil
}

func (w *DailyWriter) Close() error {
	w.mu.Lock()
	defer w.mu.Unlock()

	if w.file != nil {
		return w.file.Close()
	}
	return nil
}
