// Sample file showing Gorilla Mux patterns for the documentation generator

package main

import (
	"net/http"
	"github.com/gorilla/mux"
)

func main() {
	r := mux.NewRouter()

	// Basic Mux patterns
	r.HandleFunc("/users", getUsers).Methods("GET")
	r.HandleFunc("/users", createUser).Methods("POST")
	r.HandleFunc("/users/{id}", getUser).Methods("GET")
	r.HandleFunc("/users/{id}", updateUser).Methods("PUT")
	r.HandleFunc("/users/{id}", deleteUser).Methods("DELETE")

	// Multiple methods on same path
	r.HandleFunc("/posts", handlePosts).Methods("GET", "POST")
	r.HandleFunc("/comments", handleComments).Methods("GET", "POST", "PUT")

	// Mux Path patterns
	r.Path("/articles/{category}/{slug}").HandlerFunc(getArticle).Methods("GET")

	// Subrouters
	api := r.PathPrefix("/api/v1").Subrouter()
	api.HandleFunc("/health", healthCheck).Methods("GET")
	api.HandleFunc("/status", systemStatus).Methods("GET")

	http.Handle("/", r)
	http.ListenAndServe(":8080", nil)
}

// Handler functions
func getUsers(w http.ResponseWriter, r *http.Request) {
	// GET /users - Get all users
	w.Write([]byte("Users list"))
}

func createUser(w http.ResponseWriter, r *http.Request) {
	// POST /users - Create a new user
	w.Write([]byte("User created"))
}

func getUser(w http.ResponseWriter, r *http.Request) {
	// GET /users/{id} - Get a specific user
	vars := mux.Vars(r)
	id := vars["id"]
	w.Write([]byte("User " + id))
}

func updateUser(w http.ResponseWriter, r *http.Request) {
	// PUT /users/{id} - Update a user
	vars := mux.Vars(r)
	id := vars["id"]
	w.Write([]byte("User " + id + " updated"))
}

func deleteUser(w http.ResponseWriter, r *http.Request) {
	// DELETE /users/{id} - Delete a user
	vars := mux.Vars(r)
	id := vars["id"]
	w.Write([]byte("User " + id + " deleted"))
}

func handlePosts(w http.ResponseWriter, r *http.Request) {
	// GET/POST /posts - Handle blog posts
	if r.Method == "GET" {
		w.Write([]byte("Posts list"))
	} else if r.Method == "POST" {
		w.Write([]byte("Post created"))
	}
}

func handleComments(w http.ResponseWriter, r *http.Request) {
	// GET/POST/PUT /comments - Handle comments
	w.Write([]byte("Comments handled"))
}

func getArticle(w http.ResponseWriter, r *http.Request) {
	// GET /articles/{category}/{slug} - Get article by category and slug
	vars := mux.Vars(r)
	category := vars["category"]
	slug := vars["slug"]
	w.Write([]byte("Article: " + category + "/" + slug))
}

func healthCheck(w http.ResponseWriter, r *http.Request) {
	// GET /api/v1/health - Health check endpoint
	w.Write([]byte("OK"))
}

func systemStatus(w http.ResponseWriter, r *http.Request) {
	// GET /api/v1/status - System status
	w.Write([]byte("System running"))
}
