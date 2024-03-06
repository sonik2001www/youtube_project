import ssl
import smtplib
from  .load_django import *
from email.message import EmailMessage
from django.conf import settings


class GmailSender:
    def __init__(self) -> None:
        self.EMAIL_BACKEND = settings.EMAIL_BACKEND
        self.EMAIL_HOST = settings.EMAIL_HOST
        # self.EMAIL_PORT = settings.EMAIL_PORT
        self.EMAIL_PORT = 465
        self.EMAIL_USE_TLS = settings.EMAIL_USE_TLS
        self.EMAIL_HOST_USER = settings.EMAIL_HOST_USER
        self.EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD 
        self.default_subject = 'Your ScaleFluncer subscription [INFO]'
        # self.default_receiver = 'phoenix.egoist@gmail.com'
        # self.default_receiver = 'scalefluencer.supp@gmail.com'
        self.default_receiver = 'sonik2001www@gmail.com'


    def send_message(self, subject, receiver, content) -> None:
        em = EmailMessage()
        em['From'] = self.EMAIL_HOST_USER
        em['To'] = receiver
        em['Subject'] = subject
        em.set_content(content)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.EMAIL_HOST, self.EMAIL_PORT, context=context) as smtp:
                smtp.login(self.EMAIL_HOST_USER, self.EMAIL_HOST_PASSWORD)
                smtp.sendmail(self.EMAIL_HOST_USER, receiver, em.as_string())


    def send_plan_3days_warning(self, receiver) -> None:
        subject = self.default_subject
        content = """
            Dear customer,

            We hope this email finds you well. We wanted to inform you that your subscription with ScaleFluncer is expiring in three days.

            As a valued subscriber, we wanted to remind you to take the necessary steps to ensure uninterrupted service. Don't forget to top up your subscription or continue with your existing plan to continue enjoying our services.

            If you have any questions or need assistance, please don't hesitate to reach out to our support team. We're here to help!

            Thank you for choosing ScaleFluncer for your subscription needs. We appreciate your continued support.

            Best regards,
        """
        self.send_message(subject=subject, receiver=receiver, content=content)


    def send_plan_expired_warning(self, receiver) -> None:
        subject = self.default_subject
        content = """
            Dear customer,

            We hope this email finds you well. We wanted to inform you that your subscription with ScaleFluncer has expired.

            As a valued subscriber, we wanted to remind you to take the necessary steps to ensure uninterrupted service. Don't forget to top up your subscription or continue with your existing plan to continue enjoying our services.

            If you have any questions or need assistance, please don't hesitate to reach out to our support team. We're here to help!

            Thank you for choosing ScaleFluncer for your subscription needs. We appreciate your continued support.

            Best regards,
        """
        self.send_message(subject=subject, receiver=receiver, content=content)


    def send_feedback_from_user(self, user_email, title, category, text) -> None:
        subject = f'[CATEGORY: {category}] / [TITLE: {title}]'
        receiver = self.default_receiver
        content = f'[FROM]: {user_email}\n\n\n{text}'
        self.send_message(subject=subject, receiver=receiver, content=content)


if __name__ == '__main__':
    writer = GmailSender()
    writer.send_plan_3days_warning(receiver=writer.default_receiver)
    writer.send_plan_expired_warning(receiver=writer.default_receiver)



