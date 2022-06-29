# SMTP Server
根据 RFC 5321 实现简单的邮件服务器

## 安装
`pip install smtp_server`
## 启动SMTP Server
```
python -m smtp_sever [port]
```
不加`port`参数默认使用`25`端口


## 使用smtplib发送邮件
```python
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

msg = MIMEMultipart('related')
msg['From'] = formataddr([""]) 
msg['To'] = formataddr(["", ""]) 
msg['Subject'] = "测试邮件"
#文本信息
txt = MIMEText('Python发送邮件测试', 'plain', 'utf-8')
msg.attach(txt)

#附件信息
# attach = MIMEApplication(open(u"X.xlsx","rb").read())
# attach.add_header('Content-Disposition', 'attachment', filename='A.xlsx')
# msg.attach(attach)

server = smtplib.SMTP('127.0.0.1', 25) 
server.sendmail("faker@from-domian.com", "another-email@target-host.com", msg.as_string())
server.quit()

```

## 环境变量
   * `PYSMTP_SERVER_DOMAIN`