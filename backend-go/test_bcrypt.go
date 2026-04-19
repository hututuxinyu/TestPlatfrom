package main

import (
	"fmt"
	"golang.org/x/crypto/bcrypt"
)

func main() {
	// Test password
	password := "admin123"

	// Generate hash
	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Generated hash: %s\n", string(hash))

	// Test verification
	err = bcrypt.CompareHashAndPassword(hash, []byte(password))
	if err == nil {
		fmt.Println("Password verification: SUCCESS")
	} else {
		fmt.Printf("Password verification: FAILED - %v\n", err)
	}

	// Test with known hash
	knownHash := "$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy"
	err = bcrypt.CompareHashAndPassword([]byte(knownHash), []byte(password))
	if err == nil {
		fmt.Println("Known hash verification: SUCCESS")
	} else {
		fmt.Printf("Known hash verification: FAILED - %v\n", err)
	}
}
