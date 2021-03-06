import sendgrid
from common.settings import (SENDGRID_API_KEY,
                             SENDGRID_FROM_EMAIL,
                             SENDGRID_TO_EMAIL)
from sendgrid.helpers.mail import (Email,
                                   Content,
                                   Mail)


class SendGridTasks:

    def send2email(self, kwargs):
        subject = kwargs.get("subject")
        body = kwargs.get("body")
        sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
        from_email = Email(SENDGRID_FROM_EMAIL)
        to_email = Email(SENDGRID_TO_EMAIL)
        content = Content("text/html", body)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        return response.status_code
