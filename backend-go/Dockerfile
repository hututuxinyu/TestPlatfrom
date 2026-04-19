FROM golang:1.21-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache git

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o server ./cmd/server

FROM alpine:latest

RUN apk --no-cache add ca-certificates python3 bash nodejs

WORKDIR /root/

# Copy the binary from builder
COPY --from=builder /app/server .

# Create necessary directories
RUN mkdir -p data/uploads logs

# Expose port
EXPOSE 8011

# Run the application
CMD ["./server"]
