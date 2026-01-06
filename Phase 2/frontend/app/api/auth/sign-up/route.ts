// Signup API Route
// Creates a new user and issues a JWT token

import { NextRequest, NextResponse } from "next/server";
import * as crypto from "crypto";
import * as jwt from "jsonwebtoken";
import { userStore } from "@/lib/user-store";

function hashPassword(password: string): string {
  return crypto.createHash("sha256").update(password).digest("hex");
}

function generateUserId(): string {
  return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password, name } = body;

    // Validation
    if (!email || !password || !name) {
      return NextResponse.json(
        { error: "Email, password, and name are required" },
        { status: 400 }
      );
    }

    if (password.length < 8) {
      return NextResponse.json(
        { error: "Password must be at least 8 characters" },
        { status: 400 }
      );
    }

    // Check if user already exists
    if (userStore.has(email)) {
      return NextResponse.json(
        { error: "User with this email already exists" },
        { status: 400 }
      );
    }

    // Create user
    const userId = generateUserId();
    const passwordHash = hashPassword(password);

    userStore.set(email, {
      id: userId,
      email,
      name,
      passwordHash,
    });

    // Generate JWT token
    const secret = process.env.BETTER_AUTH_SECRET!;
    const token = jwt.sign(
      {
        sub: userId,
        user_id: userId,
        id: userId,
        email,
        name,
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
          id: userId,
          email,
          name,
        },
        session: {
          token,
          expiresAt: Date.now() + 7 * 24 * 60 * 60 * 1000, // 7 days
        },
      },
      { status: 201 }
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
    console.error("Signup error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
