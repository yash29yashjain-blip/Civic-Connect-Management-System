
from queue import Queue


def run_ipc_demo(messages=None):
    """Simulate producer-consumer IPC using a message queue."""
    if messages is None:
        messages = [
            "Complaint #101 submitted",
            "Complaint #102 assigned",
            "Complaint #103 resolved"
        ]

    channel = Queue()
    sent = []

    for message in messages:
        channel.put(message)
        sent.append(message)

    received = []
    while not channel.empty():
        received.append(channel.get())

    return {
        "mechanism": "Producer-consumer message queue",
        "sent": sent,
        "received": received,
        "successful": sent == received
    }
