// Session Check API Route
// Verifies if user has a valid session cookie

import { NextRequest, NextResponse } from "next/server";
import * as jwt from "jsonwebtoken";

export async function GET(request: NextRequest) {
  try {
    // Get the session token from cookies
    const token = request.cookies.get("better-auth.session_token")?.value;

    if (!token) {
      return NextResponse.json(
        { session: null, user: null },
        { status: 401 }
      );
    }

    // Verify the JWT token
    const secret = process.env.BETTER_AUTH_SECRET!;
    const decoded = jwt.verify(token, secret) as any;

    // Return session data
    return NextResponse.json({
      session: {
        token,
        expiresAt: decoded.exp * 1000, // Convert to milliseconds
      },
      user: {
        id: decoded.user_id || decoded.sub,
        email: decoded.email,
        name: decoded.name,
      },
    });
  } catch (error) {
    console.error("Session check error:", error);
    return NextResponse.json(
      { session: null, user: null },
      { status: 401 }
    );
  }
}
