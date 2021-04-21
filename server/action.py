import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import sys
# The mail addresses and password
sender_address = 'princetontigerlink@gmail.com'
sender_pass = 'tigerlink-cos333-2021'

def emailUser(receiver_address, name, acct_type, class_year):
    mail_content = '''Hello TigerLink User,

Your account is now registered. Here's the information you provided us:
Name: %s
Email Address: %s
Type of Account: %s
Class Year: %s

Excited to have you,
TigerLink Team
''' % (receiver_address, name, acct_type, class_year)

    print(sys.path)

    img_data = open('static/img/logo.png', 'rb').read()

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Congrats! You made a TigerLink Account.'   #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    image = MIMEImage(img_data, name='tigerlink')
    message.attach(image)

    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')

def emailStudentMatch(student_address, student_name, alum_address, alum_name, alum_classyear, alum_interests, alum_career_interests):
    mail_content = '''Hello %s,

You got a match! Here's the alum's information.
Name: %s
Email Address: %s
Class Year: %s
Interests/Organizations: %s
Career: %s

We recommend that you reach out to your alum as soon as possible. If they don't respond at first, feel free to follow up with them.
Excited to have you,
TigerLink Team
''' % (alum_name, alum_address, alum_classyear, alum_interests, alum_career_interests)

    img_data = open('static/img/logo.png', 'rb').read()

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = student_address
    message['Subject'] = 'Congrats %s! You were matched!' % (name)  #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    image = MIMEImage(img_data)
    message.attach(image)

    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')

def emailAlumMatch(student_address, student_name, alum_address, alum_name, student_class_year, student_interests, student_career_interests):
    mail_content = '''Hello %s,

You got a match! Here's the student's information.
Name: %s
Email Address: %s
Class Year: %s
Interests/Organizations: %s
Career: %s

We recommend that you reach out to your student as soon as possible. If they don't respond at first, feel free to follow up with them.
Excited to have you,
TigerLink Team
''' % (student_name, student_address, student_class_year, student_interests, student_career_interests)

    img_data = open('static/img/logo.png', 'rb').read()

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = alum_address
    message['Subject'] = 'Congrats %s! You were matched!' % (name)  #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    image = MIMEImage(img_data)
    message.attach(image)

    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')
