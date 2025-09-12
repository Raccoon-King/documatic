# Duplicate Endpoints Report

Found 15 duplicate conflicts:

## Conflict 1: GET /users

**Existing:** `getUsers` in `doc_parser_examples.go`
- Description: Sample file showing Gorilla Mux patterns for the documentation generator - Gorilla Mux Handler
**New:** `getUsers` in `doc_parser_examples.go`
- Description: Sample file showing Gorilla Mux patterns for the documentation generator - Gorilla Mux Handler
**Resolution:** Kept First

---

## Conflict 2: POST /users

**Existing:** `createUser` in `doc_parser_examples.go`
- Description: Router endpoint - Gorilla Mux Handler
**New:** `createUser` in `doc_parser_examples.go`
- Description: Router endpoint - Gorilla Mux Handler
**Resolution:** Kept First

---

## Conflict 3: GET /users/{id}

**Existing:** `getUser` in `doc_parser_examples.go`
- Description: Basic Mux patterns - Gorilla Mux Handler
**New:** `getUser` in `doc_parser_examples.go`
- Description: Basic Mux patterns - Gorilla Mux Handler
**Resolution:** Kept First

---

## Conflict 4: PUT /users/{id}

**Existing:** `updateUser` in `doc_parser_examples.go`
- Description: Basic Mux patterns - Gorilla Mux Handler
**New:** `updateUser` in `doc_parser_examples.go`
- Description: Basic Mux patterns - Gorilla Mux Handler
**Resolution:** Kept First

---

## Conflict 5: DELETE /users/{id}

**Existing:** `deleteUser` in `doc_parser_examples.go`
- Description: Basic Mux patterns - Gorilla Mux Handler
**New:** `deleteUser` in `doc_parser_examples.go`
- Description: Basic Mux patterns - Gorilla Mux Handler
**Resolution:** Kept First

---

## Conflict 6: GET /posts

**Existing:** `handlePosts` in `doc_parser_examples.go`
- Description: Basic Mux patterns - Gorilla Mux Handler
**New:** `handlePosts` in `doc_parser_examples.go`
- Description: Basic Mux patterns - Gorilla Mux Handler
**Resolution:** Kept First

---

## Conflict 7: POST /posts

**Existing:** `handlePosts` in `doc_parser_examples.go`
- Description: Basic Mux patterns - Gorilla Mux Handler
**New:** `handlePosts` in `doc_parser_examples.go`
- Description: Basic Mux patterns - Gorilla Mux Handler
**Resolution:** Kept First

---

## Conflict 8: GET /comments

**Existing:** `handleComments` in `doc_parser_examples.go`
- Description: Basic Mux patterns - Gorilla Mux Handler
**New:** `handleComments` in `doc_parser_examples.go`
- Description: Basic Mux patterns - Gorilla Mux Handler
**Resolution:** Kept First

---

## Conflict 9: POST /comments

**Existing:** `handleComments` in `doc_parser_examples.go`
- Description: Basic Mux patterns - Gorilla Mux Handler
**New:** `handleComments` in `doc_parser_examples.go`
- Description: Basic Mux patterns - Gorilla Mux Handler
**Resolution:** Kept First

---

## Conflict 10: PUT /comments

**Existing:** `handleComments` in `doc_parser_examples.go`
- Description: Basic Mux patterns - Gorilla Mux Handler
**New:** `handleComments` in `doc_parser_examples.go`
- Description: Basic Mux patterns - Gorilla Mux Handler
**Resolution:** Kept First

---

## Conflict 11: GET /health

**Existing:** `healthCheck` in `doc_parser_examples.go`
- Description: Multiple methods on same path - Gorilla Mux Handler
**New:** `healthCheck` in `doc_parser_examples.go`
- Description: Multiple methods on same path - Gorilla Mux Handler
**Resolution:** Kept First

---

## Conflict 12: GET /status

**Existing:** `systemStatus` in `doc_parser_examples.go`
- Description: Mux Path patterns - Gorilla Mux Handler
**New:** `systemStatus` in `doc_parser_examples.go`
- Description: Mux Path patterns - Gorilla Mux Handler
**Resolution:** Kept First

---

## Conflict 13: GET /users

**Existing:** `getUsers` in `doc_parser_examples.go`
- Description: Sample file showing Gorilla Mux patterns for the documentation generator - Gorilla Mux Handler
**New:** `getUsersHandler` in `router_example.go`
- Description: Router example file - contains the actual route registrations This is separate from handlers to
**Resolution:** Replaced With New

---

## Conflict 14: GET /users

**Existing:** `getUsersHandler` in `doc_parser_examples.go`
- Description: Router example file - contains the actual route registrations This is separate from handlers to
**New:** `updateUserHandler` in `router_example.go`
- Description: Standard net/http route regi
**Resolution:** Descriptions Merged

---

## Conflict 15: GET /health

**Existing:** `healthCheck` in `doc_parser_examples.go`
- Description: Multiple methods on same path - Gorilla Mux Handler
**New:** `healthHandler` in `router_example.go`
- Description: Basic routes
**Resolution:** Descriptions Merged

---

