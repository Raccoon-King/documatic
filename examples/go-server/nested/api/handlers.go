package main

import (
	"net/http"
)

// Additional handlers in nested directory
func apiHealth(w http.ResponseWriter, r *http.Request) {
	// GET /api/health - Nested directory handler
	w.Write([]byte("API Health OK"))
}

func apiData(w http.ResponseWriter, r *http.Request) {
	// GET /api/data - Another nested endpoint
	w.Write([]byte("API Data Response"))
}
