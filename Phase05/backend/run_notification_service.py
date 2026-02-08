#!/usr/bin/env python3
"""
Run the Notification Service

Simple script to start the WebSocket notification service on port 8002.

Usage:
    python run_notification_service.py
"""

import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("=" * 60)
        logger.info("Starting WebSocket Notification Service")
        logger.info("=" * 60)
        logger.info("Port: 8002")
        logger.info("WebSocket URL: ws://localhost:8002/ws/{user_id}")
        logger.info("Health Check: http://localhost:8002")
        logger.info("=" * 60)

        # Import and run
        from notification_service import app
        import uvicorn

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8002,
            log_level="info"
        )

    except KeyboardInterrupt:
        logger.info("\nShutting down notification service...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start notification service: {e}")
        sys.exit(1)
