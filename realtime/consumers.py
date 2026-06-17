"""
realtime/consumers.py

A "consumer" is the WebSocket equivalent of a Django view.
A view handles one HTTP request and returns one response.
A consumer handles an open, ongoing connection and can send/receive
messages at any time.

This first consumer is just a TEST — it doesn't touch your Slots or
Bookings models yet. Its only job is to prove the WebSocket plumbing
actually works before we build real features on top of it.

How it works:
1. A driver's frontend connects to ws://yourserver/ws/test/
2. connect() runs — we accept the connection.
3. Whenever the frontend sends a message, receive() runs — we just
   echo it back with "Echo: " in front.
4. When the frontend closes the tab, disconnect() runs.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TestConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Accept the WebSocket connection (without this, it gets rejected)
        await self.accept()
        await self.send(text_data=json.dumps({
            "message": "Connected successfully! Channels is working."
        }))

    async def disconnect(self, close_code):
        # Nothing to clean up yet for this simple test
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        incoming_message = data.get("message", "")

        # Send it right back, proving two-way communication works
        await self.send(text_data=json.dumps({
            "message": f"Echo: {incoming_message}"
        }))