from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_slot_update(charger_id, slot_id, is_booked):
    """
    Call this any time a slot's booked status changes (a booking gets
    created or cancelled). It sends a message into the "room" for
    that charger, and every connected browser watching it gets
    notified instantly via SlotConsumer.slot_update().
    """
    channel_layer = get_channel_layer()
    group_name = f"charger_{charger_id}"

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "slot_update",  # must match the method name in SlotConsumer
            "slot_id": slot_id,
            "is_booked": is_booked,
        },
    )
