import json

from channels.generic.websocket import AsyncWebsocketConsumer


class TestConsumer(AsyncWebsocketConsumer):
    """Simple test consumer used earlier to confirm Channels works.
    Safe to keep around or delete later — not used in the real feature."""

    async def connect(self):
        await self.accept()
        await self.send(
            text_data=json.dumps(
                {"message": "Connected successfully! Channels is working."}
            )
        )

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        incoming_message = data.get("message", "")
        await self.send(text_data=json.dumps({"message": f"Echo: {incoming_message}"}))


class SlotConsumer(AsyncWebsocketConsumer):
    """
    The real feature.

    A frontend connects to ws/slots/<charger_id>/ to watch live slot
    availability for ONE charging station. Everyone watching the same
    charger joins the same "group" (think: chat room named after that
    charger). Whenever a booking is made or cancelled anywhere in the
    backend, we send a message into that room, and everyone connected
    to it gets notified instantly.
    """

    async def connect(self):
        self.charger_id = self.scope["url_route"]["kwargs"]["charger_id"]
        self.group_name = f"charger_{self.charger_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def slot_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "slot_id": event["slot_id"],
                    "is_booked": event["is_booked"],
                }
            )
        )
