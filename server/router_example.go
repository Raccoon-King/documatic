// Router example file - contains the actual route registrations
// This is separate from handlers to demonstrate pattern matching

package main

import (
	"net/http"
)

// Standard net/http route registrations
func setupRoutes() {
	// Basic routes
	http.HandleFunc("/", helloHandler)
	http.HandleFunc("/users", getUsersHandler)
	http.HandleFunc("/create-user", createUserHandler)

	// REST-style routes
	http.HandleFunc("/users/", updateUserHandler) // Note: trailing slash
	http.HandleFunc("/users/delete", deleteUserHandler)

	// API routes
	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/scan", scanHandler)

	// Additional examples
	http.HandleFunc("/api/v1/users", getUsersHandler)
	http.HandleFunc("/api/v1/scan", scanHandler)
	http.HandleFunc("/api/v1/health", healthHandler)
}

// Simulate Gin-like router calls for pattern matching
func setupGinStyleRoutes() {
	// These would normally be router.GET("/users", handler)
	// but we're simulating the AST pattern matching
}

// Simulate Echo-like router calls
func setupEchoStyleRoutes() {
	// These would normally be e.GET("/users", handler)
	// but we're simulating for AST analysis
}
