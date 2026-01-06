// Signin API Route
// Authenticates a user and issues a JWT token

import { NextRequest, NextResponse } from "next/server";
import * as crypto from "crypto";
import * as jwt from "jsonwebtoken";
import { userStore } from "@/lib/user-store";

function hashPassword(password: string): string {
  return crypto.createHash("sha256").update(password).digest("hex");
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password } = body;

    // Validation
    if (!email || !password) {
      return NextResponse.json(
        { error: "Email and password are required" },
        { status: 400 }
      );
    }

    // Find user
    const user = userStore.get(email);
    if (!user) {
      return NextResponse.json(
        { error: "Invalid email or password" },
        { status: 401 }
      );
    }

    // Verify password
    const passwordHash = hashPassword(password);
    if (user.passwordHash !== passwordHash) {
      return NextResponse.json(
        { error: "Invalid email or password" },
        { status: 401 }
      );
    }

    // Generate JWT token
    const secret = process.env.BETTER_AUTH_SECRET!;
    const token = jwt.sign(
      {
        sub: user.id,
        user_id: user.id,
        id: user.id,
        email: user.email,
        name: user.name,
      },
      secret,
      {
        expiresIn: "7d",
        issuer: process.env.BETTER_AUTH_URL,
        audience: process.env.BETTER_AUTH_URL,
      }
    );

    // Set cookie
    const response = NextResponse.json(
      {
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
        },
        session: {
          token,
          expiresAt: Date.now() + 7 * 24 * 60 * 60 * 1000, // 7 days
        },
      },
      { status: 200 }
    );

    response.cookies.set("better-auth.session_token", token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: "/",
    });

    return response;
  } catch (error) {
    console.error("Signin error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
