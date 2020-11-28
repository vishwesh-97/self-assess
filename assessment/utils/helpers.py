from assessment import settings


def send_email(subject, message, to_email_list, attachment=None,
               attachment_name="", attachment_type="", bcc=None):
    from django.core.mail import EmailMessage
    from django.core.mail.backends.smtp import EmailBackend

    if settings.DEBUG:
        print("Sending Email")
    try:
        mail_host = settings.EMAIL_HOST
        mail_username = settings.EMAIL_HOST_USER
        mail_password = settings.EMAIL_HOST_PASSWORD
        mail_port = settings.EMAIL_PORT
        from_email = settings.FROM_EMAIL
        backend = EmailBackend(host=mail_host, port=mail_port,
                               username=mail_username,
                               password=mail_password, use_tls=True,
                               fail_silently=True)
        email = EmailMessage(subject=subject, body=message, from_email=from_email,
                             to=to_email_list, connection=backend, bcc=bcc)
        if attachment:
            email.attach('{}'.format(attachment_name), attachment,
                         '{}'.format(attachment_type))
        email.content_subtype = 'html'
        email.send()
        if settings.DEBUG:
            print("Email Sended")
    except:
        pass
