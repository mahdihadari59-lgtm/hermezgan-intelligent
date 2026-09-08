import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import logging
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class EmailService:
    """سرویس ارسال ایمیل"""

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None
    ):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.from_email = from_email or os.getenv("FROM_EMAIL")

        # Jinja2 محیط
        self.jinja_env = Environment(
            loader=FileSystemLoader("templates/email")
        )

    def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        ارسال ایمیل

        Args:
            to: گیرنده
            subject: موضوع
            html_content: محتوای HTML
            text_content: محتوای متن (اختیاری)
            cc: کپی
            bcc: کپی مخفی

        Returns:
            bool: موفقیت ارسال
        """
        try:
            if not self.smtp_user or not self.smtp_password:
                logger.warning("⚠️ اطلاعات SMTP تنظیم نشده است")
                return False

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to

            if cc:
                msg["Cc"] = ", ".join(cc)

            if bcc:
                msg["Bcc"] = ", ".join(bcc)

            # بخش متن
            if text_content:
                part_text = MIMEText(text_content, "plain", "utf-8")
                msg.attach(part_text)

            # بخش HTML
            part_html = MIMEText(html_content, "html", "utf-8")
            msg.attach(part_html)

            # ارسال
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)

                recipients = [to]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)

                server.send_message(msg, self.from_email, recipients)

            logger.info(f"📧 ایمیل ارسال شد به: {to}")
            return True

        except Exception as e:
            logger.error(f"❌ خطا در ارسال ایمیل: {e}")
            return False

    def send_welcome_email(self, to: str, username: str) -> bool:
        """ارسال ایمیل خوش‌آمدگویی"""
        try:
            template = self.jinja_env.get_template("welcome.html")
            html_content = template.render(username=username)

            return self.send_email(
                to=to,
                subject="🌊 به هرمزگان هوشمند خوش‌آمدید",
                html_content=html_content
            )
        except Exception as e:
            logger.error(f"❌ خطا در ارسال ایمیل خوش‌آمدگویی: {e}")
            return False

    def send_verification_email(self, to: str, token: str) -> bool:
        """ارسال ایمیل تأیید"""
        try:
            verify_url = f"{os.getenv('FRONTEND_URL')}/verify?token={token}"

            template = self.jinja_env.get_template("verify.html")
            html_content = template.render(verify_url=verify_url)

            return self.send_email(
                to=to,
                subject="✅ تأیید ایمیل - هرمزگان هوشمند",
                html_content=html_content
            )
        except Exception as e:
            logger.error(f"❌ خطا در ارسال ایمیل تأیید: {e}")
            return False

    def send_reset_password_email(self, to: str, token: str) -> bool:
        """ارسال ایمیل بازنشانی رمز عبور"""
        try:
            reset_url = f"{os.getenv('FRONTEND_URL')}/reset-password?token={token}"

            template = self.jinja_env.get_template("reset_password.html")
            html_content = template.render(reset_url=reset_url)

            return self.send_email(
                to=to,
                subject="🔑 بازنشانی رمز عبور - هرمزگان هوشمند",
                html_content=html_content
            )
        except Exception as e:
            logger.error(f"❌ خطا در ارسال ایمیل بازنشانی: {e}")
            return False
