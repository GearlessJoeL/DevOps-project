from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import random
import smtplib
    
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def run():  #return the string of verification code
    from_addr = '376627397@qq.com'
    password = 'zzcxiahvpphnbjia'
    to_addr = '2020090921011@std.uestc.edu.cn'
    smtp_server = "smtp.qq.com"
    vc = ''.join([chr(random.randint(48, 122))for i in range(4)])

    mail =  "Your varification code is %s" % vc

    msg = MIMEText(mail, 'plain', 'utf-8')
    msg['From'] = _format_addr('Administrator <%s>' % from_addr)
    msg['To'] = _format_addr('User <%s>' % to_addr)
    msg['Subject'] = Header('Your regist message', 'utf-8').encode()
        
    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(0)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()
    return vc