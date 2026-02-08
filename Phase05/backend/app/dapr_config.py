# [Task T019] Dapr client wrapper for event publishing

import os
import json
from typing import Any, Optional
from dapr.clients import DaprClient
from dapr.clients.grpc._response import DaprResponse
import logging

logger = logging.getLogger(__name__)


class DaprClientWrapper:
    """
    Wrapper for Dapr client to handle event publishing and service invocation.
    Uses Dapr SDK to interact with Dapr sidecar.
    """

    def __init__(self):
        """Initialize Dapr client."""
        self.dapr_grpc_port = os.getenv("DAPR_GRPC_PORT", "50001")
        self.dapr_http_port = os.getenv("DAPR_HTTP_PORT", "3500")
        self.pubsub_name = os.getenv("DAPR_PUBSUB_NAME", "pubsub")
        self._client: Optional[DaprClient] = None

    @property
    def client(self) -> DaprClient:
        """Get or create Dapr client instance."""
        if self._client is None:
            self._client = DaprClient(f"localhost:{self.dapr_grpc_port}")
        return self._client

    async def publish_event(
        self,
        topic: str,
        data: dict[str, Any],
        pubsub_name: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None
    ) -> None:
        """
        Publish an event to a Dapr Pub/Sub topic.

        Args:
            topic: Topic name (e.g., 'task-events', 'reminders')
            data: Event data (will be JSON serialized)
            pubsub_name: Pub/Sub component name (defaults to DAPR_PUBSUB_NAME)
            metadata: Optional CloudEvents metadata

        Raises:
            Exception: If publishing fails
        """
        pubsub = pubsub_name or self.pubsub_name

        try:
            with self.client as dapr:
                # Publish event using Dapr Pub/Sub
                dapr.publish_event(
                    pubsub_name=pubsub,
                    topic_name=topic,
                    data=json.dumps(data),
                    data_content_type="application/json",
                    metadata=metadata or {}
                )
                logger.info(f"Published event to topic '{topic}' on pubsub '{pubsub}'")

        except Exception as e:
            logger.error(f"Failed to publish event to topic '{topic}': {e}")
            raise

    async def invoke_service(
        self,
        app_id: str,
        method_name: str,
        data: Optional[dict[str, Any]] = None,
        http_verb: str = "POST"
    ) -> Any:
        """
        Invoke another service using Dapr service invocation.

        Args:
            app_id: Target service app ID
            method_name: Method/endpoint to invoke
            data: Request data (optional)
            http_verb: HTTP verb (GET, POST, etc.)

        Returns:
            Response from the invoked service
        """
        try:
            with self.client as dapr:
                response = dapr.invoke_method(
                    app_id=app_id,
                    method_name=method_name,
                    data=json.dumps(data) if data else None,
                    http_verb=http_verb
                )
                logger.info(f"Invoked service '{app_id}' method '{method_name}'")
                return response

        except Exception as e:
            logger.error(f"Failed to invoke service '{app_id}.{method_name}': {e}")
            raise

    def close(self):
        """Close the Dapr client connection."""
        if self._client:
            self._client.close()
            self._client = None


# Global Dapr client instance
dapr_client = DaprClientWrapper()
