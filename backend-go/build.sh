#!/bin/bash

# Build script for Test Platform Backend

set -e

echo "Building Test Platform Backend..."

# Clean previous builds
rm -f server

# Build the application
CGO_ENABLED=0 go build -a -installsuffix cgo -ldflags="-w -s" -o server ./cmd/server

echo "Build complete! Binary: ./server"
echo ""
echo "To run the server:"
echo "  ./server"
echo ""
echo "To build Docker image:"
echo "  docker build -t testplatform-backend ."
