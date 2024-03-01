import smtplib
import email.utils
from email.mime.text import MIMEText
import time

def send_q_email(text,qq_email='***@qq.com'):
    while True:
        message = MIMEText(text)
        message['To'] = email.utils.formataddr(('**', qq_email))
        message['From'] = email.utils.formataddr(('**', '***@qq.com'))
        message['Subject'] = text
        try:
            server = smtplib.SMTP_SSL('smtp.qq.com', 465)
            server.login('***@qq.com', '***')
            server.set_debuglevel(True)
            server.sendmail('***@qq.com',['***@qq.com'],msg=message.as_string())
        except Exception as e:
            print(f'发送失败，出现异常{e}')
            print(f'1秒后重新发送')
            time.sleep(1)
            continue
        else:
            server.quit()
            print(f'发送成功')
            break
