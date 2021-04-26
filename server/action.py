import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
    The TigerLink Team
    ''' % (receiver_address, name, acct_type, class_year)

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    # The subject line
    message['Subject'] = 'Congrats! You made a TigerLink Account.'
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
