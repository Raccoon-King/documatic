// Sample Go application to test the documentation parser
// This demonstrates basic web framework patterns for parsing

package main

import (
	"encoding/json"
	"fmt"
	"net/http"
)

// Sample data structures
type User struct {
	ID       int    `json:"id"`
	Name     string `json:"name"`
	Email    string `json:"email"`
}

type CreateUserRequest struct {
	Name  string `json:"name"`
	Email string `json:"email"`
}

// Net/HTTP example handlers
func helloHandler(w http.ResponseWriter, r *http.Request) {
	// Handle GET /
	fmt.Fprintf(w, "Hello World!")
}

func getUsersHandler(w http.ResponseWriter, r *http.Request) {
	// Handle GET /users
	users := []User{
		{ID: 1, Name: "John Doe", Email: "john@example.com"},
		{ID: 2, Name: "Jane Doe", Email: "jane@example.com"},
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(users)
}

func createUserHandler(w http.ResponseWriter, r *http.Request) {
	// Handle POST /users
	var req CreateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	user := User{
		ID:    3,
		Name:  req.Name,
		Email: req.Email,
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

func updateUserHandler(w http.ResponseWriter, r *http.Request) {
	// Handle PUT /users
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"message": "User updated"})
}

func deleteUserHandler(w http.ResponseWriter, r *http.Request) {
	// Handle DELETE /users
	w.WriteHeader(http.StatusNoContent)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	// Handle GET /health
	response := map[string]string{"status": "ok"}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func scanHandler(w http.ResponseWriter, r *http.Request) {
	// Handle POST /scan - upload and scan files
	response := map[string]string{"message": "File scanned successfully"}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}
