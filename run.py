import time
import smtplib
import datetime
import subprocess
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import yaml
from PIL import Image


class DingCard(object):
    def __init__(self):
        self.config = self.load_config()

    def load_config(self):  # 加载配置
        with open("config.yml", "r") as fo:
            config = yaml.load(fo, Loader=yaml.SafeLoader)
        return config

    def check_is_power_on(self):  # 检查是否亮屏
        process = subprocess.Popen(self.config["screenshot"].split(" "), shell=False, stdout=subprocess.PIPE)
        process.wait()
        time.sleep(10)
        process = subprocess.Popen(self.config["download"].split(" "), shell=False, stdout=subprocess.PIPE)
        process.wait()
        img = Image.open("autocard.png").convert("L")
        clrs = img.getcolors()
        if len(clrs) == 1:
            process = subprocess.Popen(self.config["power"].split(" "), shell=False, stdout=subprocess.PIPE)
            process.wait()
        subprocess.Popen(["rm", "autocard.png"], shell=False, stdout=subprocess.PIPE)

    def card(self):
        for step in self.config["steps"]:
            process = subprocess.Popen(step.split(" "), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
            if self.config["steps"].index(step) <= 5:
                time.sleep(10)
            else:
                time.sleep(5)

    def send_result_by_mail(self):
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        message = MIMEMultipart('related')
        subject = Header(now_time + '打卡')
        message['Subject'] = subject
        message['From'] = Header(self.config["sender"]["account"])
        message['To'] = self.config["reciver"]
        content = MIMEText('<html><body><img src="cid:imageid" alt="imageid"></body></html>', 'html', 'utf-8')
        message.attach(content)
        with open("./autocard.png", "rb") as fo:
            img_data = fo.read()
        img = MIMEImage(img_data)
        img.add_header('Content-ID', 'imageid')
        message.attach(img)
        try:
            server = smtplib.SMTP("smtp.sina.cn")
            server.login(self.config["sender"]["account"], self.config["sender"]["psw"])
            server.sendmail(self.config["sender"]["account"], self.config["reciver"], message.as_string())
            server.quit()
            print("打卡成功")
        except smtplib.SMTPException as e:
            print(e)
        subprocess.Popen(["rm", "./autocard.png"], shell=False, stdout=subprocess.PIPE).wait()

    def run(self):
        self.check_is_power_on()
        self.card()
        self.send_result_by_mail()


def main():
    ding = DingCard()
    ding.run()


if __name__ == '__main__':
    main()
