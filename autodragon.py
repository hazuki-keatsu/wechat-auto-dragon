import random
import re
import time
from datetime import datetime

import pyperclip
from pywinauto import Application

# 窗口默认标题
window_title = "测试"
# 轮询间隔时间，单位为秒
refresh = 2
# 轮询时间随机值
random_refresh = 1
# 窗口时间
window_time = 0.5
# 随机窗口时间
random_window_time = 0.1
# 默认接龙内容
content = "测试"
# 连续检测到几条接龙时才会自动发送接龙信息
dragon_state_repeat_time_maximum = 6
# 当检测到接龙进入接龙状态后，每次检测接龙时的间隔(秒)
dragon_state_retry_interval = 0.2
# 发接龙消息的前延迟时间(秒)，未启用
dragon_send_message_timeout = 0


class WechatAutoDragon:
    def __init__(self, title, log_out=True):
        self.title = title
        self.app = Application(backend='uia').connect(title_re=self.title)
        self.window = self.app.window(title_re=self.title)
        self.last_message = ""
        self.content = ""
        self.log_out = log_out
        self.dragon_state_repeat_time = 0

    def monitor_messages(self):
        """监控聊天窗口新消息"""
        message_list = self.window.child_window(control_type='List', found_index=0)
        messages = message_list.descendants(control_type='ListItem')

        if messages:
            latest_msg_item = messages[-1]
            return latest_msg_item
        return ""

    def is_dragon_message(self, msg):
        """判断是否为接龙消息"""
        pattern = r'#接龙.*?(\d+\. .+?(\n|$)){1,}'
        return re.search(pattern, msg, re.DOTALL)

    def generate_reply(self, msg):
        """生成接龙回复"""
        # 提取最后一条接龙编号
        last_number = max([int(n) for n in re.findall(r'^(\d+)\.', msg, re.M) if n.isdigit()] + [0])
        return f"{last_number + 1}. {self.get_user_name()}"

    def send_message(self, text):
        """发送消息"""
        input_box = self.window.child_window(control_type='Edit', found_index=0)

        pyperclip.copy(text)
        # 确保输入框已聚焦
        input_box.set_focus()
        # 使用 set_text 设置文本内容，避免输入法干扰
        input_box.type_keys('^v')
        # 触发回车键发送消息
        input_box.type_keys('{ENTER}')

    def get_user_name(self):
        """获取输入内容"""
        return self.content

    def click_button(self, item):
        """点击指定标题的按钮"""
        try:
            buttons = item.descendants(control_type="Button")
            target_button = None

            if self.log_out:
                print("找到的按钮列表：")
            for idx, btn in enumerate(buttons):
                if self.log_out:
                    print(f"按钮 {idx}: {btn.window_text()}")
                if btn.window_text() == "":  # 指定需要点击的按钮标题
                    target_button = btn
                    break
            if self.log_out:
                print("\n")

            if target_button:
                target_button.set_focus()
                target_button.click_input()
                time.sleep(random.uniform(window_time - random_window_time, window_time + random_window_time))
            else:
                print("未找到指定标题的按钮\n")
        except Exception as e:
            print(f"点击按钮失败: {str(e)}\n")

    def run(self, content):
        self.content = content
        while True:
            try:
                temp_random_time = random.uniform(refresh - random_refresh, refresh + random_refresh)
                # 获取当前时间
                current_time = datetime.now()
                formatted_current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

                last_msg_item = self.monitor_messages()
                current_msg_list = last_msg_item.descendants(control_type='Text')

                if self.log_out:
                    print("找到的文本列表：")
                    for idx, msg in enumerate(current_msg_list):
                        print(f"文本 {idx}: {msg.window_text()}")
                    print("\n")

                # current_msg = current_msg_list[0].window_text() # 该条获取不到其他人的最新信息
                # current_msg = current_msg_list[-1].window_text() # 该条也是最新信息
                current_msg = last_msg_item.window_text()

                if current_msg and current_msg != self.last_message:
                    if self.is_dragon_message(current_msg):
                        # 当检测到接龙
                        self.dragon_state_repeat_time = self.dragon_state_repeat_time + 1
                        print(f"第{self.dragon_state_repeat_time}次检测到接龙：\n{current_msg}\n\n当前时间：{formatted_current_time}\n")
                        if self.dragon_state_repeat_time < dragon_state_repeat_time_maximum:
                            # 若未到达接龙循环重复上限，则延迟一段时间后再次检测，当达到重复上限时才发送接龙
                            time.sleep(dragon_state_retry_interval)
                            continue

                        self.click_button(last_msg_item)
                        reply = self.generate_reply(current_msg)
                        self.send_message(reply)
                        print(f"已发送接龙：\n{reply}\n当前时间：{formatted_current_time}\n")
                        self.last_message = current_msg
                        break
                    else:
                        # 若未达到接龙循环重复上限时接龙信息被其他信息中断，则代表当前接龙可能已经完成，清空连续检测接龙数量重新检测
                        self.dragon_state_repeat_time = 0
                print(f"等待中...{temp_random_time:.2f}s，当前时间：{formatted_current_time}\n")
                time.sleep(temp_random_time)
            except Exception as e:
                print(f"发生错误：{str(e)}\n")
                self.dragon_state_repeat_time = 0
                time.sleep(temp_random_time)


if __name__ == "__main__":
    auto_dragon = WechatAutoDragon(window_title)
    auto_dragon.run(content)
