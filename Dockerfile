# Build
FROM golang:1.23-alpine AS builder
WORKDIR /app
COPY . .
RUN go mod download
RUN CGO_ENABLED=0 GOOS=linux go build -o collector ./cmd/collector

# Runtime
FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/collector .
COPY config/opcua.yaml ./config/
CMD ["./collector"]