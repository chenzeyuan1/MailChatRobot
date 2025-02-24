import imaplib
import email
from email.header import decode_header
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import ollama
import socket  

IMAP_SERVER = 'imap.qq.com'
IMAP_PORT = 993

SMTP_SERVER = 'smtp.qq.com'
SMTP_PORT = 465

EMAIL_ACCOUNT = 'yourQQmain@qq.com'
EMAIL_PASSWORD = 'your password'

def connect_to_email():
    # connect to IMAP server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    return mail

def send_email(to_addr, subject, body, retries=3):
    # create email object
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ACCOUNT
    msg['To'] = to_addr
    msg['Subject'] = subject

    # add email body
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # connect to SMTP server and send email
    attempt = 0
    while attempt < retries:
        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
                server.sendmail(EMAIL_ACCOUNT, to_addr, msg.as_string())
            print("Email sent successfully")
            break
        except smtplib.SMTPResponseException as e:
            print(f"SMTP error: {e.smtp_code} - {e.smtp_error}")
            attempt += 1
            time.sleep(5)  

            break

        except Exception as e:
            print(f"Unexpected error: {e}")
            attempt += 1
            time.sleep(5) 

            break

def parse_email_body(body):
    split_body = body.split("---raw mail---")
    return split_body[0] if split_body else body

def write_email_to_file(email_info, file_path='email_info.txt'):
    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f"From: {email_info['from_name']} <{email_info['from_addr']}>\n")
            f.write(f"Subject: {email_info['subject']}\n")
            f.write(f"Body: {email_info['body']}\n")
            f.write("\n" + "="*50 + "\n\n")
        
    except Exception as e:
        print(f"Failed to write email information to file: {e}")


def check_new_emails(mail, last_email_id):
    # Select the inbox
    mail.select('inbox')

    # Search for all emails
    status, messages = mail.search(None, 'ALL')
    email_ids = messages[0].split()

    # Get the latest email ID
    latest_email_id = email_ids[-1]

    # Check if there are new emails
    if latest_email_id > last_email_id:
        print("You have new emails!")
        
        # Get the email information
        status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                
                # Parse email subject
                subject, encoding = decode_header(msg['Subject'])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else 'utf-8')
                
                # Parse email sender information
                from_ = msg.get('From')
                from_name, from_addr = email.utils.parseaddr(from_)
                from_name, encoding = decode_header(from_name)[0]
                if isinstance(from_name, bytes):
                    from_name = from_name.decode(encoding if encoding else 'utf-8')
                
                # Parse email body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get('Content-Disposition'))

                        if content_type == "text/plain" and 'attachment' not in content_disposition:
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = payload.decode('utf-8', errors='ignore')
                                break
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')

                body = parse_email_body(body)
        last_email_id = latest_email_id

        email_info = {
            "from_name": from_name,
            "from_addr": from_addr,
            "subject": subject,
            "body": body
        }
        write_email_to_file(email_info,'email_info.txt')
        return email_info, last_email_id

    return None, last_email_id

def check_network_connection(host="8.8.8.8", port=53, timeout=3):
    """
    check if the network connection is available
    :param host: default check Google DNS
    :param port: port number
    :param timeout: timeout
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(f"Network connection error: {ex}")
        return False

if __name__ == '__main__':
    if not check_network_connection():
        print("Network is not available. Please check your connection.")
        exit(1)

    
    mail = connect_to_email()
    last_email_id = b'0'  
    print("Checking for new emails...")
    n = 0
    while True:
        
        new_email, last_email_id = check_new_emails(mail, last_email_id)
        if new_email:
            print(f"From: {new_email['from_name']} <{new_email['from_addr']}>")
            print(f"Subject: {new_email['subject']}")
            print(f"Body: {new_email['body']}")
            mail_info = f"You are the email management robot for Orange, a student at Southeast University. You have received an email from {new_email['from_name']} with the subject {new_email['subject']} and the body {new_email['body']}. Please reply on behalf of Orange. No need to use the email format, just reply directly."
            stream = ollama.chat(
                model='deepseek-r1:8b',
                messages=[{'role': 'user', 'content': mail_info}],
                stream=True,
            )
            ai_response = "(This mail is genereted by ai)\n"
            for chunk in stream:
                ai_response += chunk['message']['content']
                print(chunk['message']['content'], end='', flush=True)
            print('\n')
            
            send_email(new_email['from_addr'], f"Re: {new_email['subject']}", ai_response)

            
            ai_response_info = {
                "from_name": "IOrange",
                "from_addr": "1402491916@qq.com",
                "subject": f"Re: {new_email['subject']}",
                "body": ai_response
            }
            write_email_to_file(ai_response_info)
        time.sleep(1)  # Check for new emails every second
        n += 1
        if n % 60 == 0:
            print(f"Checking for new emails...{n/60}min", flush=True)    
    mail.logout()
