// Framework examples file - demonstrates different web framework patterns
// This shows the actual code patterns that the analyzer searches for

package main

// Uncommented code below would be actual framework calls:
// For Gin framework:
// r := gin.Default()
// r.GET("/gin/users", func(c *gin.Context) { ... })
// r.POST("/gin/users", func(c *gin.Context) { ... })
// etc.

// For Echo framework:
// e := echo.New()
// e.GET("/echo/users", func(c echo.Context) error { ... })

// For analysis purposes, these patterns are embedded in comments
// The analyzer currently looks for explicit method calls like:
// ginRouter.GET, echo.GET, http.HandleFunc, etc.

import "net/http"

// Additional net/http examples
func init() {
	// More examples of http.HandleFunc calls
	http.HandleFunc("/api/v2/users", getUsersHandler)
	http.HandleFunc("/api/v2/scan", scanHandler)

	// Note: The analyzer searches for calls like:
	// router.GET("/path", handler) for Gin
	// e.POST("/path", handler) for Echo
	// http.HandleFunc("/path", handler) for net/http
}

// Framework pattern examples for documentation:
// Gin Router patterns:
//   router := gin.Default()
//   router.Group("/api").GET("/users", handler)
//   router.POST("/users", handler)
//   router.PUT("/users/:id", handler)
//   router.DELETE("/users/:id", handler)
//   router.Handle("PATCH", "/users/:id", handler)
//
// Echo Router patterns:
//   e := echo.New()
//   e.GET("/users", handler)
//   e.POST("/users", handler)
//   e.PUT("/users/:id", handler)
//   e.DELETE("/users/:id", handler)
//
// Standard library http patterns:
//   http.HandleFunc("/", handler)
//   http.HandleFunc("/users", handler)
