# 自动微信接龙  

> [!WARNING]
> 由于微信4.0.0版本更换了新的UI框架——QT，同时禁用了Accessibility选项，导致这个脚本无法正常工作。所以这个仓库从2025年10月15日正式归档，请不要再使用该脚本！！

这是一个简单的自动微信接龙程序，使用Python 3.9编写。  

## 依赖  

- Python 3.9  
- pywinauto
- pyperclip
- re
- time
- random

## 使用方法  

先将微信中的群聊窗口拖出，即形成一个独立的群聊窗口，然后根据自己的需要修改autodragon.py中的参数，最后运行main.py即可。  

## 实现原理

这个程序使用了Python的pywinauto库来操作Windows系统的UI，并通过pyperclip库来复制和粘贴文本。  

程序首先获取群聊窗口的句柄，然后循环检查最近一条消息是否是接龙相关的消息，如果是，则通过pyperclip库来复制文本，并通过pywinauto库来粘贴文本，最后通过pywinauto库来发送文本；如果否，就会继续循环检测。  

本来使用pywinauto库Application中的set_text()方法来输入文本会更加方便的，但是由于群聊窗口的输入框控件无法直接替换，所以只能通过pyperclip库来复制和粘贴文本。（腾讯，你是故意的还是不小心的！）  
