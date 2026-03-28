from src.modules.email.application.dto.email_message_dto import EmailMessageDTO


class EmailDeliveryPolicy:
    def __init__(self, max_preview_chars: int = 1200) -> None:
        self._max_preview_chars = max_preview_chars

    def should_deliver(self, message: EmailMessageDTO) -> bool:
        if not message.sender.strip():
            return False
        has_text = bool(message.body_main.strip() or (message.body_signature or "").strip())
        if not message.subject.strip() and not has_text:
            return False
        return True


    def normalize(self, message: EmailMessageDTO) -> EmailMessageDTO:
        main = message.body_main.strip()
        sig = (message.body_signature or "").strip() or None

        total = len(main) + (len(sig) + 2 if sig else 0)
        if total <= self._max_preview_chars:
            return self._build_dto(message, main, sig)

        sig_cap = min(240, max(0, self._max_preview_chars // 4))
        if sig:
            if len(sig) > sig_cap:
                sig = f"{sig[: sig_cap - 3]}..." if sig_cap > 3 else None
            main_budget = self._max_preview_chars - (len(sig) + 2 if sig else 0)
        else:
            main_budget = self._max_preview_chars

        if main_budget < 1:
            main = "..."
        elif len(main) > main_budget:
            main = f"{main[: main_budget - 3]}..."

        return self._build_dto(message, main, sig)


    @staticmethod
    def _build_dto(message: EmailMessageDTO, main: str, sig: str | None) -> EmailMessageDTO:
        return EmailMessageDTO(
            uid=message.uid,
            provider=message.provider,
            message_id=message.message_id,
            subject=message.subject.strip() or "(no subject)",
            sender=message.sender.strip(),
            received_at=message.received_at,
            body_main=main,
            body_signature=sig,
            attachment_count=message.attachment_count,
        )