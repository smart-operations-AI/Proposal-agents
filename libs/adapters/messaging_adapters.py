from typing import Any, Dict, Optional
from .base import BaseMessagingAdapter

class WhatsAppAdapter(BaseMessagingAdapter):
    async def send_message(self, recipient_id: str, content: str, template_id: Optional[str] = None) -> Dict[str, Any]:
        print(f"[Messaging] WhatsApp sent to {recipient_id}: {content[:30]}...")
        return {"status": "sent", "provider": "twilio_whatsapp", "message_id": "wa_123"}

class EmailAdapter(BaseMessagingAdapter):
    async def send_message(self, recipient_id: str, content: str, template_id: Optional[str] = None) -> Dict[str, Any]:
        print(f"[Messaging] Email sent to {recipient_id}: {content[:30]}...")
        return {"status": "sent", "provider": "sendgrid", "message_id": "em_456"}
