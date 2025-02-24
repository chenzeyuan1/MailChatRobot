# Introduction
This is an email robot based on large models, using Ollama and local large models. You can configure your own email and Ollama for deployment. Subsequently, you can set appropriate prompts to assist you in handling and replying to emails.
# How to Use
## Step 1: Configure the Email Server
First, determine the type of your email and your email account. Then, query your email password. Note that this password is your key password, not the login password of your email. Usually, it can be found in the email settings - security section.
```python
IMAP_SERVER = 'imap.qq.com'
IMAP_PORT = 993

SMTP_SERVER ='smtp.qq.com'
SMTP_PORT = 465

EMAIL_ACCOUNT = 'yourQQmain@qq.com'
EMAIL_PASSWORD = 'your password'
```
Here, a QQ email is used as an example. Please make corresponding modifications in the `main` function after proper configuration.
## Step 2: Deploy Ollama
The deployment tutorial for Ollama can be searched on GitHub and will not be elaborated here.
## Step 3: Configure the `main` Function
As shown in the following program, you can configure the prompt by yourself.
```python
mail_info = f"You are the email management robot for Orange, a student at Southeast University. You have received an email from {new_email['from_name']} with the subject {new_email['subject']} and the body {new_email['body']}. Please reply on behalf of Orange. No need to use the email format, just reply directly."
stream = ollama.chat(
    model='deepseek-r1:8b',
    messages=[{'role': 'user', 'content': mail_info}],
    stream=True,
)
```
# License
MIT License 
