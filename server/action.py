import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from .keychain import KeyChain
import sys

keychain = KeyChain()
# The mail addresses and password
sender_address = 'princetontigerlink@gmail.com'
sender_pass = keychain.EMAIL_SECRET


def emailUser(receiver_address, name, acct_type, class_year):
    mail_content = '''Hello TigerLink User,

Your account is now registered. Here's the information you provided us:
Name: %s
Email Address: %s
Type of Account: %s
Class Year: %s

Excited to have you,
The TigerLink Team
    ''' % (receiver_address, name, acct_type, class_year)

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


def confirmDeletion(receiver_address):
    mail_content = '''Hello TigerLink User,

Your account has been deleted, including your posts and matches.
We're sad to see you go, but you're welcome back anytime!

Best,
The TigerLink Team
    '''

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    # The subject line
    message['Subject'] = 'Account Deletion Confirmation'
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    # login with mail_id and password
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()

def emailStudentMatch(student_address, student_name, alum_address, alum_name, alum_classyear, alum_communities, alum_careers):
    if (len(alum_communities) == 0):
        alum_communities = 'No communities entered.'
    else:
        alum_communities = " ".join(str(v) for v in alum_communities)
        
    alum_careers = " ".join(str(v) for v in alum_careers)

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
''' % (student_name, alum_name, alum_address, alum_classyear, alum_communities, alum_careers)

    img_data = open('static/img/logo.png', 'rb').read()

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = student_address
    message['Subject'] = 'Congrats %s! You were matched!' % (student_name)  #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    image = MIMEImage(img_data, name='tigerlink-logo')
    message.attach(image)

    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, student_address, text)
    session.quit()
    print('Mail Sent')

def emailAlumMatch(student_address, student_name, alum_address, alum_name, student_class_year, student_communities, student_careers):
    if (len(student_communities) == 0):
        student_communities = 'No communities entered.'
    else:
        student_communities = " ".join(str(v) for v in student_communities)
        
    student_careers = " ".join(str(v) for v in student_careers)

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
''' % (alum_name, student_name, student_address, student_class_year, student_communities, student_careers)

    img_data = open('static/img/logo.png', 'rb').read()

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = alum_address
    message['Subject'] = 'Congrats %s! You were matched!' % (alum_name)  #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    image = MIMEImage(img_data, name='tigerlink-logo')
    message.attach(image)

    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, alum_address, text)
    session.quit()
    print('Mail Sent')
