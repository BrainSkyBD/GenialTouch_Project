from django.core.mail import send_mail

def send_email_function(subject, message, from_mail, to_mails_list):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_mail,
            recipient_list=to_mails_list,
            fail_silently=False,
        )
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

    
