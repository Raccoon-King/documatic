# Grabby-Documatic

Version 1.0

A documentation generation and parsing project.

## Features

- **Go Source Code Analyzer**: Automatically parses Go source files to extract API endpoints and generate documentation
- **Multi-Framework Support**: Native support for Gin, Echo, Gorilla Mux, and net/http frameworks
- **Live Server Inspection**: Connect to running Go servers to capture real JSON data shapes and request/response examples
- **Markdown Documentation**: Generate comprehensive, visually enhanced API documentation with curl examples
- **Recursive File Scanning**: Analyze entire Go projects with automatic sub-directory discovery
- **Self-Documenting**: Can analyze its own example Go server to demonstrate capabilities

## Getting Started

### Prerequisites

- Python 3.7+
- Go 1.19+ (optional, for testing with live server inspection)

### Installation

No installation required! Just download and run:

```bash
git clone https://github.com/Raccoon-King/grabby-documatic.git
cd grabby-documatic
python doc_generator.py --help
```

## Usage

### Basic Usage

Generate API documentation from any Go project:

```bash
# Analyze current directory
python doc_generator.py .

# Analyze specific directory
python doc_generator.py /path/to/your/go/project

# Generate documentation with live server inspection
python doc_generator.py . --inspect-server 8080
```

### Command Line Options

- `directory`: Go project directory to analyze (default: current directory)
- `--inspect-server [port]`: Attach to running Go server on specified port for data shape inspection
- `--no-recursive`: Disable recursive directory scanning

### Example Usage

```bash
# Analyze the included example Go server
python doc_generator.py examples/go-server

# Analyze with live server data (if server is running on port 9090)
python doc_generator.py examples/go-server --inspect-server 9090

# Quick test of any Go web API
python doc_generator.py /path/to/my/go/api --inspect-server 3000
```

## Supported Frameworks

### ✅ Framework Compatibility

- **Gin**: `router.GET/POST/PUT/DELETE("/path", handler)`
- **Echo**: `e.GET/POST/PUT/DELETE("/path", handler)`
- **Gorilla Mux**: `r.HandleFunc("/path", handler).Methods("GET")`
- **net/http**: `http.HandleFunc("/path", handler)`

### 🔧 Framework Detection

The analyzer automatically detects and parses:
- Direct router method calls
- Group-based routing patterns
- Handler function comments and documentation
- Request/response data structures
- HTTP method definitions

## Output

Generates comprehensive `apidocs.md` with:

### 📊 Analysis Summary
- Total endpoints discovered
- HTTP method distribution
- Framework usage statistics
- Documentation coverage metrics

### 🔗 Per-Endpoint Documentation
- Complete curl examples for testing
- HTTP method and path information
- Handler function references
- Auto-generated example data structures

### 🎯 Live Data Inspection Results
When connected to a running server:
- Real JSON request/response examples
- Actual data shape validation
- Server compatibility verification

### 📈 Example Output

```markdown
# 🚀 API Documentation

## 📊 API Overview
| Metric | Value |
|---|---|
| 🔗 Total Endpoints | 12 |
| 📁 Route Groups | 3 |
| 🔧 HTTP Methods | 4 |

### HTTP Method Distribution
🟢 GET: 8 | 🔵 POST: 2 | 🟡 PUT: 1 | 🔴 DELETE: 1

## 🔧 Detailed Endpoint Documentation
- 🟢 GET `/users` - Get all users
- 🔵 POST `/users` - Create new user
- 🟡 PUT `/users/{id}` - Update user
- 🔴 DELETE `/users/{id}` - Delete user
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
