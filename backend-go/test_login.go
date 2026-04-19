package main

import (
	"context"
	"fmt"
	"github.com/jackc/pgx/v5/pgxpool"
	"golang.org/x/crypto/bcrypt"
)

func main() {
	// Connect to database
	connStr := "postgres://postgres:1234@localhost:5432/testplatform?sslmode=disable"
	pool, err := pgxpool.New(context.Background(), connStr)
	if err != nil {
		panic(err)
	}
	defer pool.Close()

	// Get user
	var username, passwordHash string
	var isActive bool
	err = pool.QueryRow(context.Background(), 
		"SELECT username, password_hash, is_active FROM users WHERE username = $1", 
		"admin").Scan(&username, &passwordHash, &isActive)
	
	if err != nil {
		fmt.Printf("Error getting user: %v\n", err)
		return
	}

	fmt.Printf("Username: %s\n", username)
	fmt.Printf("Is Active: %v\n", isActive)
	fmt.Printf("Password Hash: %s\n", passwordHash)

	// Test password
	password := "admin123"
	err = bcrypt.CompareHashAndPassword([]byte(passwordHash), []byte(password))
	if err == nil {
		fmt.Println("✓ Password verification: SUCCESS")
	} else {
		fmt.Printf("✗ Password verification: FAILED - %v\n", err)
	}
}
