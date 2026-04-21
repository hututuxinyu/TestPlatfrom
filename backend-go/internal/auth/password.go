package auth

// CheckPassword compares a plain text password with stored password
func CheckPassword(password, storedPassword string) bool {
	return password == storedPassword
}
