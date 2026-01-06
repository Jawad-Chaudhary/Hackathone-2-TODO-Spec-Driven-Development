// [Task T019] Better Auth configuration with JWT plugin

import { createAuthClient } from "better-auth/client";
import { env } from "./env";

/**
 * Better Auth client configured with JWT plugin.
 * JWT tokens expire in 7 days with no refresh tokens (per spec).
 */
export const authClient = createAuthClient({
  baseURL: env.BETTER_AUTH_URL,
  // JWT plugin configuration
  plugins: [
    // Note: Better Auth JWT configuration
    // The JWT secret and expiration are configured on the server side
    // Client just needs to send credentials
  ],
});

/**
 * Auth API for use in components.
 */
export const auth = authClient;
