package main

import (
	"log"
	"net/http"
	"os"
)

var OPENAI_API_KEY, PHOENIX_API_KEY string
var OPENAI_API_URL, PHOENIX_API_URL string

func init() {
	OPENAI_API_KEY = os.Getenv("OPENAI_API_KEY")
	if OPENAI_API_KEY == "" {
		log.Fatal("OPENAI_API_KEY is not set")
	}

	PHOENIX_API_KEY = os.Getenv("PHOENIX_API_KEY")
	if PHOENIX_API_KEY == "" {
		log.Fatal("PHOENIX_API_KEY is not set")
	}

	OPENAI_API_URL = os.Getenv("OPENAI_API_URL")
	if OPENAI_API_URL == "" {
		log.Fatal("OPENAI_API_URL is not set")
	}

	PHOENIX_API_URL = os.Getenv("PHOENIX_API_URL")
	if PHOENIX_API_URL == "" {
		log.Fatal("PHOENIX_API_URL is not set")
	}
}

func main() {
	router := http.NewServeMux()
	router.HandleFunc("/health", healthHandler)
	router.HandleFunc("/v1/complete", completeHandler)

	server := &http.Server{
		Addr:    "localhost:14200",
		Handler: router,
	}

	log.Printf("Starting server on http://%s", server.Addr)
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("Server error: %v", err)
	}

}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE")
	w.Header().Set("Access-Control-Allow-Headers", "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")
	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	w.WriteHeader(http.StatusOK)
	w.Write([]byte("OK"))
}

func completeHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE")
	w.Header().Set("Access-Control-Allow-Headers", "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")
	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	w.WriteHeader(http.StatusNotImplemented)
	w.Write([]byte("Not implemented yet"))
}
