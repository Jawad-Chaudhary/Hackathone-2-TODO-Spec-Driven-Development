// Better Auth API Route Handler
// This catch-all route handles all Better Auth authentication requests

import { auth } from "@/lib/auth-server";

export const GET = auth.handler;
export const POST = auth.handler;
