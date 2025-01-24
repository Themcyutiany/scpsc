import argparse
import socket
import os
import threading
import sys
import time  # 导入 time 模块用于计时

# 定义缓冲区大小
BUFFER_SIZE = 4096

def start_server(ip, port):
    """
    启动服务器
    """
    try:
        # 创建TCP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, port))  # 绑定IP和端口
        server_socket.listen(1)  # 监听连接，最多允许1个客户端连接
        server_socket.settimeout(1)  # 设置超时时间为1秒
        print(f"服务器已启动，正在监听 {ip}:{port} ...")
        print("按 Ctrl + C 终止监听。")
        # 标志位，用于控制服务器循环
        running = True

        def handle_client(client_socket, client_address):
            """
            处理客户端连接
            """
            try:
                print(f"客户端已连接: {client_address}")
                # 接收文件名长度
                file_name_length = int.from_bytes(client_socket.recv(4), byteorder='big')
                # 接收文件名
                file_name = client_socket.recv(file_name_length).decode('utf-8')
                print(f"正在接收文件: {file_name}")
                # 接收文件大小
                file_size = int.from_bytes(client_socket.recv(8), byteorder='big')
                file_size_mb = file_size / (1024 * 1024)  # 将文件大小转换为 MB
                print(f"文件大小: {file_size_mb:.2f} MB")
                # 接收文件内容
                received_bytes = 0
                start_time = time.time()  # 记录开始时间
                with open(file_name, "wb") as file:
                    while received_bytes < file_size:
                        data = client_socket.recv(BUFFER_SIZE)
                        if not data:
                            break
                        file.write(data)
                        received_bytes += len(data)
                        # 计算传输速度、已用时间和预计剩余时间
                        elapsed_time = time.time() - start_time  # 已用时间（秒）
                        if elapsed_time > 0:
                            speed = (received_bytes / (1024 * 1024)) / elapsed_time  # 传输速度（MB/s）
                            remaining_bytes = file_size - received_bytes
                            remaining_time = remaining_bytes / (speed * 1024 * 1024)  # 剩余时间（秒）
                        else:
                            speed = 0
                            remaining_time = 0
                        # 打印进度条、速度、已用时间和剩余时间
                        progress = (received_bytes / file_size) * 100
                        sys.stdout.write(
                            f"\r接收进度: [{progress:.2f}%] | 速度: {speed:.2f} MB/s | "
                            f"已用时间: {elapsed_time:.2f} 秒 | 预计剩余时间: {remaining_time:.2f} 秒"
                        )
                        sys.stdout.flush()
                print(f"\n文件接收完成: {file_name}")
            except Exception as e:
                print(f"文件接收失败: {e}")
            finally:
                client_socket.close()
                print(f"客户端 {client_address} 已断开连接")

        # 主循环，等待客户端连接
        while running:
            try:
                client_socket, client_address = server_socket.accept()
                # 启动一个新线程处理客户端
                client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
                client_thread.daemon = True  # 设置为守护线程
                client_thread.start()
            except socket.timeout:
                continue  # 超时后继续循环
            except KeyboardInterrupt:
                print("\n服务器正在关闭...")
                running = False  # 终止循环
    except Exception as e:
        print(f"服务器发生错误: {e}")
    finally:
        # 关闭服务器 socket
        server_socket.close()
        print("服务器已关闭")

def start_client(ip, port, file_path):
    """
    启动客户端
    """
    try:
        # 创建TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))  # 连接到服务器
        print(f"已连接到服务器 {ip}:{port}")
        # 发送文件名长度
        file_name = os.path.basename(file_path)
        file_name_length = len(file_name.encode('utf-8'))
        client_socket.send(file_name_length.to_bytes(4, byteorder='big'))
        # 发送文件名
        client_socket.send(file_name.encode('utf-8'))
        # 发送文件大小
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)  # 将文件大小转换为 MB
        client_socket.send(file_size.to_bytes(8, byteorder='big'))
        print(f"文件大小: {file_size_mb:.2f} MB")
        # 发送文件内容
        sent_bytes = 0
        start_time = time.time()  # 记录开始时间
        with open(file_path, "rb") as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    break
                client_socket.send(data)
                sent_bytes += len(data)
                # 计算传输速度、已用时间和预计剩余时间
                elapsed_time = time.time() - start_time  # 已用时间（秒）
                if elapsed_time > 0:
                    speed = (sent_bytes / (1024 * 1024)) / elapsed_time  # 传输速度（MB/s）
                    remaining_bytes = file_size - sent_bytes
                    remaining_time = remaining_bytes / (speed * 1024 * 1024)  # 剩余时间（秒）
                else:
                    speed = 0
                    remaining_time = 0
                # 打印进度条、速度、已用时间和剩余时间
                progress = (sent_bytes / file_size) * 100
                sys.stdout.write(
                    f"\r发送进度: [{progress:.2f}%] | 速度: {speed:.2f} MB/s | "
                    f"已用时间: {elapsed_time:.2f} 秒 | 预计剩余时间: {remaining_time:.2f} 秒"
                )
                sys.stdout.flush()
        print(f"\n文件发送完成: {file_name}")
    except KeyboardInterrupt:
        print("\n客户端正在关闭...")
    except Exception as e:
        print(f"文件发送失败: {e}")
    finally:
        # 关闭连接
        client_socket.close()
        print("客户端已关闭")

def main():
    """
    主函数，解析命令行参数
    """
    parser = argparse.ArgumentParser(description="简单的客户端-服务器通信程序")
    parser.add_argument('-ser', action='store_true', help="启动服务器")
    parser.add_argument('-cli', action='store_true', help="启动客户端")
    parser.add_argument('--ip', type=str, default='127.0.0.1', help="IP地址 (默认: 127.0.0.1)")
    parser.add_argument('--port', type=int, default=12345, help="端口号 (默认: 12345)")
    parser.add_argument('--file', type=str, help="要传输的文件路径")
    args = parser.parse_args()
    if args.ser:
        start_server(args.ip, args.port)
    elif args.cli:
        if not args.file:
            print("错误：客户端模式需要指定文件路径 (--file)")
            return
        start_client(args.ip, args.port, args.file)
    else:
        parser.print_help()  # 如果没有指定模式，打印帮助信息

if __name__ == "__main__":
    main()