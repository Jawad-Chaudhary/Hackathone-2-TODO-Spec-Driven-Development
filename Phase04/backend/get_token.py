#!/usr/bin/env python
"""Generate a JWT token for testing API endpoints."""

import jwt
from datetime import datetime, timedelta
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

def generate_token(user_id: str = "test_user", days_valid: int = 7) -> str:
    """
    Generate a JWT token for testing.

    Args:
        user_id: The user ID to encode in the token (string)
        days_valid: Number of days the token should be valid

    Returns:
        JWT token string
    """
    SECRET = os.getenv("BETTER_AUTH_SECRET")

    if not SECRET:
        print("ERROR: BETTER_AUTH_SECRET not found in .env")
        print("Make sure backend/.env file exists and contains BETTER_AUTH_SECRET")
        return None

    token = jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.utcnow() + timedelta(days=days_valid)
        },
        SECRET,
        algorithm="HS256"
    )

    return token


if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("JWT Token Generator")
    print("=" * 70)

    # Get user ID from command line or prompt
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        print(f"\nUsing user ID: {user_id}")
    else:
        user_id_input = input("\nEnter user ID (default: test_user): ").strip()
        user_id = user_id_input if user_id_input else "test_user"

    # Generate token
    token = generate_token(user_id)

    if token:
        print(f"\n[+] Token generated successfully for user {user_id}")
        print(f"[+] Valid for 7 days")
        print("\n" + "=" * 70)
        print("TOKEN:")
        print("=" * 70)
        print(token)
        print("=" * 70)

        print("\n" + "=" * 70)
        print("USAGE:")
        print("=" * 70)
        print("\n1. Copy the token above")
        print("\n2. Use in API requests:")
        print(f"   Authorization: Bearer {token[:30]}...")

        print("\n3. Test with cURL:")
        print(f"""
   curl -X POST http://localhost:8000/api/{user_id}/chat \\
     -H "Content-Type: application/json" \\
     -H "Authorization: Bearer {token}" \\
     -d '{{"message": "Add a task: Test task"}}'
        """)

        print("\n4. Or use in Postman/Insomnia:")
        print("   - Method: POST")
        print(f"   - URL: http://localhost:8000/api/{user_id}/chat")
        print("   - Header: Authorization: Bearer <token>")
        print("   - Body: {\"message\": \"Add a task: Test task\"}")
        print("\n" + "=" * 70)
    else:
        print("\n[X] Failed to generate token")
        print("Check that BETTER_AUTH_SECRET is set in backend/.env")
