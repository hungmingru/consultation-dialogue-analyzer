"""
Cloud API client for syncing conversation data.
"""

import requests
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from app.cloud_config import CLOUD_API_URL, CLOUD_API_KEY, CLOUD_API_SECRET, SYNC_BATCH_SIZE, SYNC_TIMEOUT, SYNC_CURSOR_FILE

logger = logging.getLogger(__name__)


class CloudAPIClient:
    """Client for cloud conversation sync API."""

    def __init__(self):
        self.base_url = CLOUD_API_URL
        self.api_key = CLOUD_API_KEY
        self.api_secret = CLOUD_API_SECRET
        self.cursor_file = Path(SYNC_CURSOR_FILE)
        self.cursor_file.parent.mkdir(parents=True, exist_ok=True)

    def get_cursor(self) -> Optional[str]:
        """Get the last sync cursor from local file."""
        if not self.cursor_file.exists():
            return None
        
        try:
            with open(self.cursor_file, "r") as f:
                data = json.load(f)
                return data.get("cursor")
        except Exception as e:
            logger.error(f"Failed to read cursor: {e}")
            return None

    def save_cursor(self, cursor: str) -> None:
        """Save the sync cursor to local file."""
        try:
            with open(self.cursor_file, "w") as f:
                json.dump({
                    "cursor": cursor,
                    "timestamp": datetime.utcnow().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cursor: {e}")

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "X-API-Key": self.api_key,
            "X-API-Secret": self.api_secret,
            "Content-Type": "application/json",
        }

    def fetch_conversations(self, cursor: Optional[str] = None, limit: int = None) -> Dict[str, Any]:
        """
        Fetch conversations from cloud API.
        
        Args:
            cursor: Last sync cursor for incremental sync
            limit: Max number of records to fetch (default SYNC_BATCH_SIZE)
        
        Returns:
            {
                "success": bool,
                "data": List[Dict],  # List of conversation records
                "cursor": str,        # Next cursor for pagination
                "has_more": bool,     # Whether more data exists
                "count": int          # Number of records returned
            }
        """
        if limit is None:
            limit = SYNC_BATCH_SIZE

        try:
            url = f"{self.base_url}/api/v1/conversations/sync"
            params = {
                "limit": limit,
            }
            if cursor:
                params["cursor"] = cursor

            logger.info(f"Fetching conversations from cloud API with cursor={cursor}")
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=SYNC_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"Fetched {len(data.get('data', []))} conversations")
            return {
                "success": True,
                "data": data.get("data", []),
                "cursor": data.get("cursor"),
                "has_more": data.get("has_more", False),
                "count": len(data.get("data", []))
            }
        except requests.RequestException as e:
            logger.error(f"Cloud API request failed: {e}")
            return {
                "success": False,
                "data": [],
                "cursor": cursor,
                "has_more": False,
                "count": 0,
                "error": str(e)
            }

    def fetch_all_conversations(self, max_batches: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch all conversations using pagination.
        
        Args:
            max_batches: Maximum number of batches to fetch (for testing)
        
        Returns:
            List of all conversation records
        """
        all_data = []
        cursor = self.get_cursor()
        batch_count = 0

        while True:
            if max_batches and batch_count >= max_batches:
                break

            result = self.fetch_conversations(cursor)
            
            if not result["success"]:
                logger.error(f"Failed to fetch conversations: {result.get('error')}")
                break

            all_data.extend(result["data"])
            logger.info(f"Batch {batch_count + 1}: {result['count']} records")
            batch_count += 1

            if not result["has_more"]:
                # Save the last cursor for next sync
                if result["cursor"]:
                    self.save_cursor(result["cursor"])
                    logger.info(f"Saved cursor for next sync: {result['cursor']}")
                break

            cursor = result["cursor"]

        logger.info(f"Total fetched: {len(all_data)} conversations in {batch_count} batches")
        return all_data
