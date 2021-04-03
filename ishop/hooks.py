from account.hooks import AccountDefaultHookSet
import hashlib
import random
from django.core.mail import send_mail
from django.template.loader import render_to_string
from account.conf import settings


class AccountHookSet(AccountDefaultHookSet):
    def send_confirmation_email(self, to, ctx):
        subject = render_to_string(
            "account/email/email_confirmation_subject.txt", ctx)
        subject = "".join(subject.splitlines())
        message = render_to_string(
            "account/email/email_confirmation_message.txt", ctx)
        html_message = render_to_string(
            "account/email/email_confirmation_message.html", ctx)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                  to, html_message=html_message)

    def send_password_change_email(self, to, ctx):
        subject = render_to_string(
            "account/email/password_change_subject.txt", ctx)
        subject = "".join(subject.splitlines())
        message = render_to_string("account/email/password_change.txt", ctx)
        html_message = render_to_string(
            "account/email/password_change.html", ctx)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                  to, html_message=html_message)

    def send_password_reset_email(self, to, ctx):
        subject = render_to_string(
            "account/email/password_reset_subject.txt", ctx)
        subject = "".join(subject.splitlines())
        message = render_to_string("account/email/password_reset.txt", ctx)
        html_message = render_to_string(
            "account/email/password_reset.html", ctx)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                  to, html_message=html_message)
