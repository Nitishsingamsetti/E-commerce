import smtplib
from smtplib import SMTP 
from email.message import EmailMessage
def sendmail(email,subject,body):
    server=smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('232niti@gmail.com','orjh rxmj qqxq ldlz')
    msg=EmailMessage()
    msg['FROM']='232niti@gmail@gmail.com'
    msg['TO']=email
    msg['SUBJECT']=subject
    msg.set_content(body)
    server.send_message(msg)
    server.quit()