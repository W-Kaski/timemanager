import tkinter as tk
from cgitb import small
from operator import ifloordiv
from tkinter import ttk, messagebox
import time
import random
import threading
from playsound import playsound
import os


class TimeManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("时间管理大师")
        self.root.geometry("600x400")

        # 初始化声音文件路径
        self.sound_dir = "sounds"
        self.start_break_sound = os.path.join(self.sound_dir, "start_break.mp3")
        self.end_break_sound = os.path.join(self.sound_dir, "end_break.mp3")
        self.major_cycle_end_sound = os.path.join(self.sound_dir, "major_cycle_end.mp3")

        # 状态变量
        self.current_thread = None
        self.current_cycle_type = "学习"

        self.current_state = ""
        self.current_study_type = True
        self.remaining_small_cycles = 0
        self.remaining_time = 0
        self.create_widgets()

    def create_widgets(self):
        # 大周期设置框架
        major_frame = ttk.LabelFrame(self.root, text="大周期设置", padding="10")
        major_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(major_frame, text="学习时间（分钟）:").grid(row=0, column=0, sticky="w")
        self.study_time = ttk.Entry(major_frame, width=10)
        self.study_time.insert(0, "90")
        self.study_time.grid(row=0, column=1, padx=5)

        ttk.Label(major_frame, text="休息时间（分钟）:").grid(row=1, column=0, sticky="w")
        self.break_time = ttk.Entry(major_frame, width=10)
        self.break_time.insert(0, "20")
        self.break_time.grid(row=1, column=1, padx=5)

        # 小周期设置框架
        small_frame = ttk.LabelFrame(self.root, text="小周期设置", padding="10")
        small_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(small_frame, text="学习时间范围（分钟）:").grid(row=0, column=0, sticky="w")
        self.min_study = ttk.Entry(small_frame, width=5)
        self.min_study.insert(0, "5")
        self.min_study.grid(row=0, column=1, padx=5)

        ttk.Label(small_frame, text="至").grid(row=0, column=2)
        self.max_study = ttk.Entry(small_frame, width=5)
        self.max_study.insert(0, "10")
        self.max_study.grid(row=0, column=3, padx=5)

        ttk.Label(small_frame, text="休息时间（秒）:").grid(row=1, column=0, sticky="w")
        self.small_break = ttk.Entry(small_frame, width=10)
        self.small_break.insert(0, "10")
        self.small_break.grid(row=1, column=1, columnspan=3, padx=5)

        # 状态显示
        status_frame = ttk.LabelFrame(self.root, text="当前状态", padding="10")
        status_frame.pack(fill="x", padx=10, pady=5)

        self.time_label = ttk.Label(status_frame, text="待开始", font=("Arial", 20))
        self.time_label.pack()

        self.status_label = ttk.Label(status_frame, text="")
        self.status_label.pack()

        # 控制按钮
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill="x", padx=10, pady=5)

        self.start_button = ttk.Button(control_frame, text="开始", command=self.start)
        self.start_button.pack(side="left", padx=5)

        self.pause_button = ttk.Button(control_frame, text="暂停", command=self.pause, state="disabled")
        self.pause_button.pack(side="left", padx=5)

        self.reset_button = ttk.Button(control_frame, text="重置", command=self.reset)
        self.reset_button.pack(side="left", padx=5)

    def play_sound(self, sound_file):
        """播放提示音"""
        try:
            playsound(sound_file)
        except Exception as e:
            print(f"播放声音时出错: {e}")

    def update_time_display(self, seconds, is_major_cycle=False):
        """更新时间显示"""
        minutes, secs = divmod(seconds, 60)
        if is_major_cycle:
            self.time_label.config(text=f"{self.current_cycle_type}周期 进度: {minutes:02d}分{secs:02d}秒")
        else:
            if self.current_cycle_type == "学习":
                cycle_type = "学习" if self.current_study_type else "休息"
                self.status_label.config(text=f"{cycle_type}小周期剩余时间: {minutes:02d}分{secs:02d}秒")

    def start(self):
        """开始计时"""
        self.current_state = "running"
        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal")

        self.run_cycles()

    def pause(self):
        """暂停计时"""
        self.current_state = "pause"
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")

    def reset(self):
        """重置所有状态"""
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self.time_label.config(text="待开始")
        self.status_label.config(text="")
        # 重置所有计时相关的状态
        self.remaining_time = 0
        self.remaining_small_cycles = 0
        self.current_cycle_type = "学习"
        self.current_state = ""

    def run_cycles(self):
        """运行周期"""

        def run_timer():
            while self.current_state != "":
                try:
                    if self.current_state == "pause":
                        time.sleep(0.1)  # 暂停状态下休眠100ms
                        continue
                        
                    elif self.current_cycle_type == "学习":
                        # 学习周期
                        study_mins = float(self.study_time.get())
                        self.run_study_cycle(study_mins * 60)

                        if self.current_state == "":
                            return
                    elif self.current_cycle_type == "休息":
                        # 休息周期
                        break_mins = float(self.break_time.get())
                        self.run_break_cycle(break_mins * 60)

                        if self.current_state == "":
                            return
                    # 只在正常完成周期时播放音效，而不是在重置后
                    if self.remaining_time == 0 and self.current_state == "running":
                        self.play_sound(self.major_cycle_end_sound)

                except ValueError as e:
                    messagebox.showerror("错误", "请输入有效的数字！")
                    self.reset()
                    break
                except Exception as e:
                    messagebox.showerror("错误", f"发生错误: {str(e)}")
                    self.reset()
                    break

        # 在新线程中运行计时器
        self.current_thread = threading.Thread(target=run_timer)
        self.current_thread.daemon = True
        self.current_thread.start()

    def run_study_cycle(self, duration):
        """运行学习周期"""
        self.current_cycle_type = "学习"

        if self.remaining_time != 0:
            duration = int(self.remaining_time)  # 确保是整数
            if self.remaining_small_cycles == 0 and self.current_study_type:
                min_study = int(float(self.min_study.get()) * 60)  # 直接转换为秒数的整数
                max_study = int(float(self.max_study.get()) * 60)  # 直接转换为秒数的整数
                small_cycle_time = random.randint(min_study, max_study)

            elif self.remaining_small_cycles == 0 and not self.current_study_type:
                small_cycle_time = int(float(self.small_break.get()))  # 转换为整数
            else:
                small_cycle_time = int(self.remaining_small_cycles)  # 确保是整数
        else:
            min_study = int(float(self.min_study.get()) * 60)  # 直接转换为秒数的整数
            max_study = int(float(self.max_study.get()) * 60)  # 直接转换为秒数的整数
            small_cycle_time = random.randint(min_study, max_study)
            self.current_study_type = True

        if small_cycle_time > duration:
            small_cycle_time = duration

        if self.current_study_type:
            # 学习时间倒计时
            for i in range(0, small_cycle_time + 1, 1):  # 修改为倒计时方式，包含0秒
                if self.current_state == "pause":
                    self.current_study_type = True
                    self.current_cycle_type = "学习"
                    return
                elif self.current_state == "":
                    return

                self.remaining_time = duration - i
                self.remaining_small_cycles = small_cycle_time - i
                self.update_time_display(int(self.remaining_time), True)
                self.update_time_display(self.remaining_small_cycles, False)
                time.sleep(1)

            # 播放开始休息音效
            if self.remaining_time != 0:
                self.play_sound(self.start_break_sound)
                self.current_study_type = False

        else:

            # 休息时间倒计时
            for i in range(0, int(small_cycle_time) + 1, 1):
                if self.current_state == "pause":
                    self.current_study_type = False
                    self.current_cycle_type = "学习"
                    return
                elif self.current_state == "":
                    return

                self.remaining_time = duration - i
                self.remaining_small_cycles = small_cycle_time - i
                self.update_time_display(int(self.remaining_time), True)
                self.update_time_display(int(self.remaining_small_cycles), False)
                time.sleep(1)


            # 播放结束休息音效
            if self.remaining_time != 0:
                self.play_sound(self.end_break_sound)
                self.current_study_type = True

        if self.remaining_time == 0 :
            self.current_cycle_type = "休息"

    def run_break_cycle(self, duration):
        """运行休息周期"""

        self.status_label.config(text="")  # 清空小周期状态显示

        if self.remaining_time != 0:
            try:
                duration = self.remaining_time
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字！")
                self.reset()
                return

        # 休息时间倒计时
        for i in range(0, int(duration) + 1, 1):
            if self.current_state == "pause":
                self.current_cycle_type = "休息"
                return
            elif self.current_state == "":
                return
            self.remaining_time = duration - i
            self.update_time_display(int(self.remaining_time), True)
            time.sleep(1)

        if self.remaining_time == 0:
            self.current_cycle_type = "学习"


def main():
    root = tk.Tk()
    app = TimeManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
