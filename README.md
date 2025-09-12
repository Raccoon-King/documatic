# Grabby-Documatic

```
 ██████╗ ██████╗  █████╗ ██████╗ ██████╗ ██╗   ██╗
██╔════╝ ██╔══██╗██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝
██║  ███╗██████╔╝███████║██████╔╝██████╔╝ ╚████╔╝ 
██║   ██║██╔══██╗██╔══██║██╔══██╗██╔══██╗  ╚██╔╝  
╚██████╔╝██║  ██║██║  ██║██████╔╝██████╔╝   ██║   
 ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═════╝    ╚═╝   
                                                   
██████╗  ██████╗  ██████╗██╗   ██╗███╗   ███╗ █████╗ ████████╗██╗ ██████╗
██╔══██╗██╔═══██╗██╔════╝██║   ██║████╗ ████║██╔══██╗╚══██╔══╝██║██╔════╝
██║  ██║██║   ██║██║     ██║   ██║██╔████╔██║███████║   ██║   ██║██║     
██║  ██║██║   ██║██║     ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██║██║     
██████╔╝╚██████╔╝╚██████╗╚██████╔╝██║ ╚═╝ ██║██║  ██║   ██║   ██║╚██████╗
╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝
```

**Version 2.0** - 🚀 Your Go API Documentation Generator 📚

An intelligent, interactive documentation generation system for Go web APIs with advanced duplicate detection and conflict resolution.

## ✨ New Features (v2.0)

### 🎯 **Interactive Menu System**
- Beautiful ASCII art interface
- Guided step-by-step process
- No command-line arguments needed
- User-friendly prompts and confirmations

### 🔍 **Advanced Duplicate Detection**
- **Smart Conflict Resolution**: Multiple strategies for handling duplicate endpoints
- **Detailed Reporting**: Comprehensive duplicate analysis with resolution breakdowns  
- **Real-time Feedback**: Immediate alerts when conflicts are detected
- **File Tracking**: Know exactly which files contain which endpoints

### 🛡️ **Enhanced Security & Validation**
- Input sanitization and validation
- XSS prevention in generated documentation
- Path normalization and security checks
- Robust error handling with graceful degradation

### ⚡ **Performance Optimizations**
- Compiled regex patterns for faster processing
- Improved memory usage
- Enhanced comment filtering
- Better file parsing with encoding detection

## 🚀 Core Features

- **🔧 Multi-Framework Support**: Gin, Echo, Gorilla Mux, net/http
- **📡 Live Server Inspection**: Real-time API data shape capture
- **🎨 Beautiful Documentation**: Visually enhanced markdown with emojis and styling
- **🔄 Recursive Scanning**: Automatic sub-directory discovery
- **📊 Statistical Analysis**: Detailed metrics and summaries
- **🎯 Endpoint Validation**: Comprehensive endpoint verification

## 🚦 Getting Started

### Prerequisites

- **Python 3.7+** (Required)
- **Go 1.19+** (Optional, for live server inspection)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Raccoon-King/grabby-documatic.git
cd grabby-documatic

# Run the interactive menu
python doc_generator.py
```

That's it! The interactive menu will guide you through the rest.

## 📖 Usage

### Interactive Menu Options

When you run `python doc_generator.py`, you'll see:

```
📋 What would you like to do?
1. 📁 Analyze Go project directory
2. 🔬 Analyze with live server inspection  
3. 📊 Generate duplicate endpoints report
4. ⚙️ Advanced settings
5. ❓ Help & Info
6. 🚪 Exit
```

### Quick Examples

#### Basic Analysis
1. Run `python doc_generator.py`
2. Select option `1` (Analyze Go project directory)
3. Enter your project path or press Enter for current directory
4. Confirm the analysis
5. View the generated `apidocs.md`

#### Live Server Inspection
1. Start your Go server (e.g., on port 8080)
2. Run `python doc_generator.py`
3. Select option `2` (Analyze with live server inspection)
4. Enter your project directory
5. Enter server port (8080)
6. Get enhanced documentation with real API responses!

#### Duplicate Analysis
1. Run `python doc_generator.py`  
2. Select option `3` (Generate duplicate endpoints report)
3. Check the generated `duplicates_report.md` for detailed conflict analysis

## 🔧 Advanced Settings

Access advanced configuration through the settings menu (option 4):

### 🔄 Recursive Scanning
- **Enabled (default)**: Scans all subdirectories
- **Disabled**: Only scans the specified directory

### 📝 Duplicate Resolution Strategies
1. **Keep First** (default): Preserve the first endpoint found
2. **Replace with New**: Use endpoint with better description
3. **Merge Descriptions**: Combine information from both endpoints

### 🎯 Custom Output Files
- Configure API documentation filename
- Set duplicate report filename
- Customize output locations

## 🎨 Supported Frameworks

### ✅ Framework Compatibility

| Framework | Pattern Support | Status |
|-----------|-----------------|--------|
| **Gin** | `router.GET/POST("/path", handler)` | ✅ Full Support |
| **Echo** | `e.GET/POST("/path", handler)` | ✅ Full Support |
| **Gorilla Mux** | `r.HandleFunc("/path", handler)` | ✅ Full Support |
| **net/http** | `http.HandleFunc("/path", handler)` | ✅ Full Support |

### 🔍 Smart Detection Features
- **Automatic Framework Recognition**: No configuration needed
- **Comment Filtering**: Ignores commented-out code
- **Group Route Support**: Handles nested routing patterns
- **Handler Documentation**: Extracts function comments
- **Parameter Detection**: Identifies path parameters (`:id`, `{id}`)

## 📊 Output Files

### 🚀 `apidocs.md` - Main Documentation
Comprehensive API documentation with:
- **Visual Headers**: Emoji-enhanced sections
- **Statistical Summaries**: Endpoint counts and method distribution
- **Interactive Examples**: Ready-to-use curl commands
- **Data Shapes**: Real or inferred request/response structures
- **Detailed Descriptions**: Extracted from code comments

### 📈 `duplicates_report.md` - Conflict Analysis
Detailed duplicate endpoint analysis:
- **Conflict Detection**: Lists all duplicate endpoints found
- **Resolution Details**: Shows how each conflict was resolved
- **File Tracking**: Identifies source files for each endpoint
- **Statistics**: Summary of duplicate patterns

### 📋 Example Outputs

#### Main Documentation Structure
```markdown
# 🚀 API Documentation

**Status**: Ready 100.00% • 📅 2024-01-15 14:30:22

## 📊 API Overview
| Metric | Value |
|--------|-------|
| 🔗 Total Endpoints | 15 |
| 📁 Route Groups | 4 |
| 🔧 HTTP Methods | 5 |

📊 Duplicate Analysis:
• Unique endpoints: 15
• Duplicates detected: 3
• Duplicates skipped: 3
✅ No duplicate endpoints detected

🟢 GET: 8 | 🔵 POST: 4 | 🟡 PUT: 2 | 🔴 DELETE: 1
```

#### Duplicate Report Structure
```markdown
# Duplicate Endpoints Report

Found 2 duplicate conflicts:

## Conflict 1: GET /api/users
**Existing:** `getUsersHandler` in `handlers.go`
- Description: Fetch all users from database

**New:** `listUsers` in `api.go`  
- Description: Returns user list with pagination

**Resolution:** Descriptions Merged
```

## 🛠️ Development & Troubleshooting

### 🐛 Common Issues

#### "No API endpoints found"
- Ensure Go files contain recognizable routing patterns
- Check that files aren't in excluded directories (`.git`, `node_modules`, `vendor`)
- Verify your project structure matches supported frameworks

#### Server inspection fails
- Confirm your Go server is running on the specified port
- Check that the server accepts HTTP requests
- Ensure no firewall is blocking connections

#### Duplicate detection too aggressive
- Adjust resolution strategy in Advanced Settings
- Check for legitimate endpoint variations
- Review generated duplicate report for details

### 📋 File Structure
```
grabby-documatic/
├── doc_generator.py          # Main application
├── README.md                 # This documentation
├── examples/                 # Example Go server
│   └── go-server/           # Demo application
├── apidocs.md               # Generated documentation (output)
└── duplicates_report.md     # Duplicate analysis (output)
```

### 🔧 Extending Grabby-Documatic

#### Adding New Frameworks
1. Add regex patterns in `_extract_*_routes()` methods
2. Update framework detection logic
3. Test with sample code patterns

#### Custom Output Formats
1. Modify `generate_markdown_docs()` function
2. Add new template variables
3. Update documentation structure

## 🚨 Security Notes

- **Input Validation**: All paths and inputs are validated and sanitized
- **XSS Prevention**: HTML tags are stripped from descriptions
- **Path Traversal**: Directory traversal attempts are blocked
- **Resource Limits**: Large files (>10MB) are automatically skipped

## 🤝 Contributing

We welcome contributions! Areas of interest:
- **New Framework Support**: Add support for additional Go web frameworks
- **Output Formats**: JSON, YAML, or other documentation formats
- **UI Improvements**: Enhanced interactive experience
- **Performance**: Further optimization of parsing algorithms

## 📈 Changelog

### Version 2.0 (Latest)
- ✨ Interactive menu system with ASCII art
- 🔍 Advanced duplicate detection and resolution
- 🛡️ Enhanced security and validation  
- ⚡ Performance optimizations
- 📊 Comprehensive reporting system

### Version 1.0
- Basic Go code analysis
- Multi-framework support
- Live server inspection
- Markdown documentation generation

## 💡 Tips & Best Practices

### 📝 Writing Better API Comments
```go
// GetUsers retrieves all users with optional pagination
// Supports filtering by role and status parameters
func GetUsers(c *gin.Context) {
    // handler implementation
}
```

### 🏗️ Organizing Your Go Project
- Group related endpoints in separate files
- Use consistent naming conventions
- Add meaningful comments to handlers
- Keep routing logic separate from business logic

### 🔍 Effective Duplicate Management
- Use descriptive handler function names
- Avoid identical paths across different files
- Leverage the merge descriptions strategy for related endpoints
- Regular duplicate analysis during development

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
