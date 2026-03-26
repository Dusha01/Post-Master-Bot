from src.modules.email.application.dto.email_message_dto import EmailMessageDTO


class EmailDeliveryPolicy:
    def __init__(self, max_preview_chars: int = 1200) -> None:
        self._max_preview_chars = max_preview_chars

    def should_deliver(self, message: EmailMessageDTO) -> bool:
        if not message.sender.strip():
            return False
        if not message.subject.strip() and not message.body_preview.strip():
            return False
        return True

    def normalize(self, message: EmailMessageDTO) -> EmailMessageDTO:
        preview = message.body_preview.strip()
        if len(preview) > self._max_preview_chars:
            preview = f"{preview[: self._max_preview_chars - 3]}..."

        return EmailMessageDTO(
            uid=message.uid,
            provider=message.provider,
            message_id=message.message_id,
            subject=message.subject.strip() or "(no subject)",
            sender=message.sender.strip(),
            received_at=message.received_at,
            body_preview=preview,
        )