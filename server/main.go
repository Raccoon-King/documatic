package main

import (
	"encoding/json"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"log"
	"net/http"
	"os"
	"strings"
)

// APIDocumentation represents the structure of API documentation
type APIDocumentation struct {
	Path        string       `json:"path"`
	Method      string       `json:"method"`
	Description string       `json:"description"`
	DataShapes  []DataShape  `json:"data_shapes,omitempty"`
	CurlExample string       `json:"curl_example"`
}

// DataShape represents request/response data structures
type DataShape struct {
	Name        string `json:"name"`
	Description string `json:"description"`
	Shape       string `json:"shape"`
}

// Analyzer analyzes Go source files for API endpoints
type Analyzer struct {
	fset    *token.FileSet
	enpoints []APIDocumentation
}

// NewAnalyzer creates a new analyzer instance
func NewAnalyzer() *Analyzer {
	return &Analyzer{
		fset: token.NewFileSet(),
	}
}

// ParseDirectory parses all .go files in a directory
func (a *Analyzer) ParseDirectory(dir string) error {
	pkgs, err := parser.ParseDir(a.fset, dir, func(info os.FileInfo) bool {
		return !strings.HasSuffix(info.Name(), "_test.go")
	}, parser.ParseComments)
	if err != nil {
		return err
	}

	for _, pkg := range pkgs {
		for _, file := range pkg.Files {
			a.analyzeFile(file)
		}
	}
	return nil
}

// analyzeFile analyzes a single Go file for API endpoints
func (a *Analyzer) analyzeFile(file *ast.File) {
	ast.Inspect(file, func(n ast.Node) bool {
		switch x := n.(type) {
		case *ast.CallExpr:
			a.extractHTTPCalls(x)
			a.extractGinRoutes(x)
			a.extractEchoRoutes(x)
		}
		return true
	})
}

// extractHTTPCalls extracts endpoints from net/http package calls
func (a *Analyzer) extractHTTPCalls(call *ast.CallExpr) {
	if fun, ok := call.Fun.(*ast.SelectorExpr); ok {
		if pkg, ok := fun.X.(*ast.Ident); ok && pkg.Name == "http" {
			if fun.Sel.Name == "HandleFunc" && len(call.Args) >= 2 {
				path := a.extractStringArg(call.Args[0])
				desc := a.findHandlerComment(call.Args[1])

				doc := APIDocumentation{
					Path:        path,
					Method:      "GET", // HandleFunc typically handles GET
					Description: desc,
					CurlExample: fmt.Sprintf("curl %s", path),
				}

				if path != "" {
					a.enpoints = append(a.enpoints, doc)
				}
			}
		}
	}
}

// extractGinRoutes extracts endpoints from Gin framework
func (a *Analyzer) extractGinRoutes(call *ast.CallExpr) {
	// Gin.GROUP().METHOD calls: router.Group("/api").POST("/users", handler)
	// or router.POST("/users", handler)

	// Check for router method calls like GET, POST, PUT, DELETE
	methods := []string{"GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"}
	for _, method := range methods {
		if fun, ok := call.Fun.(*ast.SelectorExpr); ok && fun.Sel.Name == method {
			if len(call.Args) >= 2 {
				path := a.extractStringArg(call.Args[0])
				desc := a.findHandlerComment(call.Args[1])

				doc := APIDocumentation{
					Path:        path,
					Method:      method,
					Description: desc,
					CurlExample: fmt.Sprintf("curl -X %s %s", method, path),
				}

				if path != "" {
					a.enpoints = append(a.enpoints, doc)
				}
			}
		}
	}

	// Handle Gin router.Handle calls
	if fun, ok := call.Fun.(*ast.SelectorExpr); ok && fun.Sel.Name == "Handle" {
		if len(call.Args) >= 3 {
			method := a.extractStringArg(call.Args[0])
			path := a.extractStringArg(call.Args[1])
			desc := a.findHandlerComment(call.Args[2])

			doc := APIDocumentation{
				Path:        path,
				Method:      method,
				Description: desc,
				CurlExample: fmt.Sprintf("curl -X %s %s", method, path),
			}

			if path != "" && method != "" {
				a.enpoints = append(a.enpoints, doc)
			}
		}
	}
}

// extractEchoRoutes extracts endpoints from Echo framework
func (a *Analyzer) extractEchoRoutes(call *ast.CallExpr) {
	// Echo method calls like e.POST("/users", handler)
	methods := []string{"GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"}
	for _, method := range methods {
		if fun, ok := call.Fun.(*ast.SelectorExpr); ok && fun.Sel.Name == method {
			if len(call.Args) >= 2 {
				path := a.extractStringArg(call.Args[0])
				desc := a.findHandlerComment(call.Args[1])

				doc := APIDocumentation{
					Path:        path,
					Method:      method,
					Description: desc,
					CurlExample: fmt.Sprintf("curl -X %s %s", method, path),
				}

				if path != "" {
					a.enpoints = append(a.enpoints, doc)
				}
			}
		}
	}
}

// Helper functions
func (a *Analyzer) extractStringArg(arg ast.Expr) string {
	if lit, ok := arg.(*ast.BasicLit); ok && lit.Kind == token.STRING {
		// Remove quotes from string literal
		return strings.Trim(lit.Value, `"`)
	}
	return ""
}

func (a *Analyzer) extractHandlerName(arg ast.Expr) string {
	if ident, ok := arg.(*ast.Ident); ok {
		return ident.Name
	}
	if sel, ok := arg.(*ast.SelectorExpr); ok {
		return sel.Sel.Name // Extract just the function name
	}
	return ""
}

func (a *Analyzer) findHandlerComment(arg ast.Expr) string {
	// This is a simplified implementation - in a real application,
	// you'd need to parse the comment groups associated with the function
	return "Handler function"
}

// GetEndpoints returns the collected endpoints
func (a *Analyzer) GetEndpoints() []APIDocumentation {
	return a.enpoints
}

func main() {
	analyzer := NewAnalyzer()

	// Analyze the current directory
	err := analyzer.ParseDirectory(".")
	if err != nil {
		log.Printf("Error analyzing directory: %v", err)
	}

	// Setup HTTP server
	http.HandleFunc("/analyze", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		dir := r.URL.Query().Get("dir")
		if dir == "" {
			dir = "." // Default to current directory
		}

		analyzer := NewAnalyzer()
		err := analyzer.ParseDirectory(dir)
		if err != nil {
			http.Error(w, fmt.Sprintf("Error analyzing directory: %v", err), http.StatusInternalServerError)
			return
		}

		endpoints := analyzer.GetEndpoints()
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(endpoints)
	})

	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		response := map[string]string{"status": "ok"}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	})

	http.HandleFunc("/docs", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")

		docs := []APIDocumentation{
			{
				Path:        "/analyze",
				Method:      "POST",
				Description: "Analyze a Go project and generate API documentation",
				DataShapes: []DataShape{
					{
						Name:        "Response",
						Description: "Array of API endpoints with documentation",
						Shape:       "[{\"path\":\"/endpoint\",\"method\":\"GET\",\"description\":\"Description\",\"curl_example\":\"curl /endpoint\"}]",
					},
				},
				CurlExample: "curl -X POST \"http://localhost:9090/analyze?dir=./project\"",
			},
			{
				Path:        "/health",
				Method:      "GET",
				Description: "Health check endpoint",
				DataShapes: []DataShape{
					{
						Name:        "Response",
						Description: "JSON indicating service status",
						Shape:       "{\"status\":\"ok\"}",
					},
				},
				CurlExample: "curl http://localhost:9090/health",
			},
			{
				Path:        "/docs",
				Method:      "GET",
				Description: "Returns API documentation for this service",
				CurlExample: "curl http://localhost:9090/docs",
			},
		}

		json.NewEncoder(w).Encode(docs)
	})

	fmt.Println("Documentation generator running on http://localhost:9090")
	fmt.Println("Endpoints:")
	fmt.Println("  POST /analyze?dir=./path/to/go/project - Generate API docs")
	fmt.Println("  GET  /health - Health check")
	fmt.Println("  GET  /docs - This service's documentation")

	log.Fatal(http.ListenAndServe(":9090", nil))
}
