from datetime import datetime, timezone
from email import message_from_bytes
from email.header import decode_header, make_header
from email.message import Message
from email.utils import parsedate_to_datetime

from src.modules.email.application.dto.email_message_dto import EmailMessageDTO


class MimeParser:
    def to_dto(self, *, provider: str, uid: int, raw_email: bytes) -> EmailMessageDTO:
        msg = message_from_bytes(raw_email)
        subject = self._decode_header(msg.get("Subject", ""))
        sender = self._decode_header(msg.get("From", ""))
        message_id = msg.get("Message-ID", str(uid)).strip() or str(uid)
        received_at = self._parse_date(msg.get("Date"))
        raw_body = self._extract_text_preview(msg)
        body_main, body_signature = self._split_body_and_signature(raw_body)
        attachment_count = self._count_attachments(msg)

        return EmailMessageDTO(
            uid=uid,
            provider=provider,
            message_id=message_id,
            subject=subject,
            sender=sender,
            received_at=received_at,
            body_main=body_main,
            body_signature=body_signature,
            attachment_count=attachment_count,
        )


    @staticmethod
    def _decode_header(value: str) -> str:
        try:
            return str(make_header(decode_header(value))).strip()
        except Exception:
            return value.strip()


    @staticmethod
    def _parse_date(value: str | None) -> datetime:
        if not value:
            return datetime.now(tz=timezone.utc)
        try:
            dt = parsedate_to_datetime(value)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return datetime.now(tz=timezone.utc)


    def _extract_text_preview(self, msg: Message) -> str:
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                disposition = str(part.get("Content-Disposition", ""))
                if content_type == "text/plain" and "attachment" not in disposition:
                    payload = part.get_payload(decode=True) or b""
                    charset = part.get_content_charset() or "utf-8"
                    return self._decode_payload(payload, charset)

            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    payload = part.get_payload(decode=True) or b""
                    charset = part.get_content_charset() or "utf-8"
                    return self._decode_payload(payload, charset)
            return ""

        payload = msg.get_payload(decode=True) or b""
        charset = msg.get_content_charset() or "utf-8"
        return self._decode_payload(payload, charset)


    @staticmethod
    def _decode_payload(payload: bytes, charset: str) -> str:
        try:
            return payload.decode(charset, errors="replace").strip()
        except Exception:
            return payload.decode("utf-8", errors="replace").strip()


    @staticmethod
    def _split_body_and_signature(text: str) -> tuple[str, str | None]:
        """Split RFC 3676-style signature (line with '-- ')."""
        normalized = text.replace("\r\n", "\n")
        for sep in ("\n-- \n", "\n--\n"):
            if sep in normalized:
                main, sig = normalized.split(sep, 1)
                main = main.strip()
                sig = sig.strip()
                return main, sig if sig else None
        if " -- " in normalized and "\n" not in normalized.strip():
            main, sig = normalized.split(" -- ", 1)
            main = main.strip()
            sig = sig.strip()
            if main and sig and len(sig) >= 16:
                return main, sig
        return normalized.strip(), None


    @staticmethod
    def _count_attachments(msg: Message) -> int:
        count = 0
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            disp = part.get_content_disposition()
            ctype = part.get_content_type()
            filename = part.get_filename()
            if disp == "attachment":
                count += 1
                continue
            if not filename:
                continue
            if ctype in ("text/plain", "text/html"):
                continue
            if disp == "inline" and ctype.startswith("image/"):
                continue
            count += 1
        return count