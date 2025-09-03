# Grabby-Documatic

Version 1.0

A documentation generation and parsing project.

## Features

- **API Documentation Generator**: Automatically generate API documentation by analyzing Go source code
- **Web Framework Support**: Supports Gin, Echo, and net/http frameworks
- **REST API Server**: Includes built-in HTTP server with multiple endpoints
- **JSON Documentation Format**: Outputs clean JSON documentation with curl examples
- **Health Check Endpoint**: Built-in health monitoring

## Getting Started

### Prerequisites

- Go 1.19 or later

### Server Installation

```bash
# Navigate to the server directory
cd server

# Download dependencies
go mod tidy

# Run the documentation server
go run main.go
```

The server will start on `http://localhost:9090`

## Usage

### API Endpoints

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/analyze?dir=./path/to/go/project` | POST | Generate API docs for a Go project | `curl -X POST "http://localhost:9090/analyze?dir=./server"` |
| `/health` | GET | Health check | `curl http://localhost:9090/health` |
| `/docs` | GET | Get this API's documentation | `curl http://localhost:9090/docs` |

### CLI Usage

```bash
# Start the server
cd server && go run main.go

# The server will output available endpoints:
# POST /analyze?dir=./path/to/go/project - Generate API docs
# GET  /health - Health check
# GET  /docs - This service's documentation
```

### Example Output

```json
[
  {
    "path": "/users",
    "method": "GET",
    "description": "Get all users",
    "curl_example": "curl -X GET /users"
  },
  {
    "path": "/users",
    "method": "POST",
    "description": "Create a new user",
    "curl_example": "curl -X POST /users"
  }
]
```

## License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
