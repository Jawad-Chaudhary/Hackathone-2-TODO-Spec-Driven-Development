// [Task T005] Frontend environment variable validation

/**
 * Validates required environment variables at application startup.
 * Throws a clear error if any required variable is missing.
 */
export function validateEnv() {
  const required = {
    BETTER_AUTH_SECRET: process.env.BETTER_AUTH_SECRET,
    BETTER_AUTH_URL: process.env.BETTER_AUTH_URL,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  };

  const missing: string[] = [];

  for (const [key, value] of Object.entries(required)) {
    if (!value) {
      missing.push(key);
    }
  }

  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables:\n${missing.map(k => `  - ${k}`).join('\n')}\n\n` +
      `Please copy .env.local.example to .env.local and fill in the required values.`
    );
  }
}

/**
 * Typed environment variables object.
 * Call validateEnv() before accessing these values.
 */
export const env = {
  BETTER_AUTH_SECRET: process.env.BETTER_AUTH_SECRET!,
  BETTER_AUTH_URL: process.env.BETTER_AUTH_URL!,
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL!,
} as const;
