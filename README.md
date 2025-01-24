# scpsc
中文文档:
基于python的小型文件传输工具（跨平台）为了方便日常使用

使用-h 可以查看帮助
usage: scpsc.py [-h] [-ser] [-cli] [--ip IP] [--port PORT] [--file FILE]

简单的客户端-服务器通信程序

options:
  -h, --help   show this help message and exit
  -ser         启动服务器
  -cli         启动客户端
  --ip IP      IP地址 (默认: 127.0.0.1)
  --port PORT  端口号 (默认: 12345)
  --file FILE  要传输的文件路径
  
英语文档:
usage: scpsc.py [-h] [-ser] [-cli] [--ip IP] [--port PORT] [--file FILE]

A simple client-server communication program.

options:
  -h, --help   Show this help message and exit.
  -ser         Start the server.
  -cli         Start the client.
  --ip IP      IP address (default: 127.0.0.1).
  --port PORT  Port number (default: 12345).
  --file FILE  Path to the file to be transferred.
