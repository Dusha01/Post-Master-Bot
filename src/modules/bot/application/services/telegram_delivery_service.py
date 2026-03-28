import html
import re

from src.modules.bot.application.dto.telegram_message_dto import TelegramMessageDTO
from src.modules.bot.application.ports.telegram_gateway import TelegramGatewayPort
from src.modules.email.application.dto.email_message_dto import EmailMessageDTO


class TelegramDeliveryService:
    _HTML_PARSE_MODE = "HTML"

    def __init__(self, gateway: TelegramGatewayPort, default_chat_id: str) -> None:
        self._gateway = gateway
        self._default_chat_id = default_chat_id

    async def send_email_notification(self, email_message: EmailMessageDTO) -> None:
        provider_label = self._sanitize_line(email_message.provider).upper()
        sender = self._sanitize_line(email_message.sender)
        subject = self._sanitize_line(email_message.subject)
        body_main = self._format_body_html(email_message.body_main)
        body_sig = (
            self._format_body_html(email_message.body_signature)
            if email_message.body_signature
            else None
        )
        attachment_note = self._format_attachment_note(email_message.attachment_count)

        lines: list[str] = [
            f"<b>NEW EMAIL FROM {html.escape(provider_label)}</b>",
            "",
            f"From: {html.escape(sender)}",
            f"Theme: {html.escape(subject)}",
        ]
        if attachment_note:
            lines.extend(["", attachment_note])
        lines.append("")
        if body_main:
            lines.append(body_main)
        else:
            lines.append("<i>(empty body)</i>")
        if body_sig:
            lines.extend(["", body_sig])

        text = "\n".join(lines)
        telegram_message = TelegramMessageDTO(
            chat_id=self._default_chat_id,
            text=text,
            parse_mode=self._HTML_PARSE_MODE,
        )
        await self._gateway.send_message(telegram_message)

    @staticmethod
    def _sanitize_line(value: str) -> str:
        return " ".join(value.split()).strip()

    @staticmethod
    def _format_body_html(raw: str) -> str:
        text = html.unescape(raw)
        text = re.sub(r"<[^>]+>", " ", text)
        text = text.replace("\r\n", "\n").strip()
        if not text:
            return ""
        parts = [html.escape(p) for p in text.split("\n")]
        return "<br>".join(parts)

    @staticmethod
    def _format_attachment_note(count: int) -> str | None:
        if count <= 0:
            return None
        if count == 1:
            return "📎 <i>Вложение: 1 файл</i>"
        n = abs(count) % 100
        if 11 <= n <= 14:
            word = "файлов"
        else:
            m = n % 10
            if m == 1:
                word = "файл"
            elif 2 <= m <= 4:
                word = "файла"
            else:
                word = "файлов"
        return f"📎 <i>Вложения: {count} {word}</i>"
