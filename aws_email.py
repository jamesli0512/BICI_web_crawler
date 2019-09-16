# from django.core.mail import send_mail
# from email_info import *
# import os
# from django.conf import settings

# settings.configure()

# EMAIL_USE_TLS = EMAIL_USE_TLS
# EMAIL_HOST = EMAIL_HOST
# EMAIL_HOST_USER = EMAIL_HOST_USER
# EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD
# EMAIL_PORT = EMAIL_PORT

# send_mail(
#     'Subject here',
#     'Here is the message.',
#     EMAIL_HOST_USER,
#     [EMAIL_HOST_USER],
#     fail_silently=False,
# )


# import smtplib
 
# server = smtplib.SMTP('smtp.gmail.com', 587)
# server.starttls()
# server.login("bicinorthca@gmail.com", "biciinfo31415926")
 
# msg = "YOUR MESSAGE!"
# server.sendmail("bicinorthca@gmail.com", "bicinorthca@gmail.com", msg)
# server.quit()


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
 
fromaddr = "bicinorthca@gmail.com"
toaddr = "bicinorthca@gmail.com"
 
msg = MIMEMultipart()
 
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "SUBJECT OF THE EMAIL"
 
body = "TEXT YOU WANT TO SEND"
 
msg.attach(MIMEText(body, 'plain'))
 
filename = "report.pdf"
attachment = open("/Users/shujianwen/downloads/report.pdf", "rb")
 
part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
 
msg.attach(part)
 
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, "passwordhere")
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()
