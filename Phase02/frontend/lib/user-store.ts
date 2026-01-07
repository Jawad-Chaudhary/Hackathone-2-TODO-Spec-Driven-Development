// Shared in-memory user store for authentication
// In production, this would be replaced with a database

export interface User {
  id: string;
  email: string;
  name: string;
  passwordHash: string;
}

// In-memory store
export const userStore = new Map<string, User>();
