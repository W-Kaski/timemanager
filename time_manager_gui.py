import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
import threading
from playsound import playsound
import os


class TimeManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("时间管理工具")
        self.root.geometry("600x400")

        # 初始化声音文件路径
        self.sound_dir = "sounds"
        self.start_break_sound = os.path.join(self.sound_dir, "start_break.mp3")
        self.end_break_sound = os.path.join(self.sound_dir, "end_break.mp3")
        self.major_cycle_end_sound = os.path.join(self.sound_dir, "major_cycle_end.mp3")

        # 状态变量
        self.is_running = False
        self.current_thread = None
        self.remaining_time = 0
        self.current_cycle_type = ""

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
        self.min_study.insert(0, "4")
        self.min_study.grid(row=0, column=1, padx=5)

        ttk.Label(small_frame, text="至").grid(row=0, column=2)
        self.max_study = ttk.Entry(small_frame, width=5)
        self.max_study.insert(0, "6")
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
            cycle_type = "学习" if self.current_cycle_type == "学习" else "休息"
            self.time_label.config(text=f"{cycle_type}周期 进度: {minutes:02d}分{secs:02d}秒")
        else:
            if self.current_cycle_type == "学习":
                self.status_label.config(text=f"学习小周期剩余时间: {minutes:02d}分{secs:02d}秒")

    def start(self):
        """开始计时"""
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state="disabled")
            self.pause_button.config(state="normal")

            if not self.current_thread or not self.current_thread.is_alive():
                self.current_thread = threading.Thread(target=self.run_cycles)
                self.current_thread.daemon = True
                self.current_thread.start()

    def pause(self):
        """暂停计时"""
        self.is_running = False
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")

    def reset(self):
        """重置所有状态"""
        self.is_running = False
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self.time_label.config(text="待开始")
        self.status_label.config(text="")
        self.remaining_time = 0

    def run_cycles(self):
        """运行周期"""
        while True:
            try:
                # 学习周期
                study_mins = float(self.study_time.get())
                self.run_study_cycle(study_mins * 60)

                if not self.is_running:
                    break

                # 休息周期
                break_mins = float(self.break_time.get())
                self.run_break_cycle(break_mins * 60)

                if not self.is_running:
                    break

            except ValueError as e:
                messagebox.showerror("错误", "请输入有效的数字！")
                self.reset()
                break
            except Exception as e:
                messagebox.showerror("错误", f"发生错误: {str(e)}")
                self.reset()
                break

    def run_study_cycle(self, duration):
        """运行学习周期"""
        self.current_cycle_type = "学习"
        start_time = time.time()

        while self.is_running:
            try:
                min_study = float(self.min_study.get())
                max_study = float(self.max_study.get())
                small_break = float(self.small_break.get())
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字！")
                self.reset()
                return

            study_time = random.randint(int(min_study * 60), int(max_study * 60))
            
            if study_time > duration:
                study_time = duration

            # 学习时间倒计时
            for i in range(study_time, 0, -1):
                if not self.is_running:
                    return
                remaining = duration - (time.time() - start_time)
                if remaining > 0:
                    self.update_time_display(int(remaining), True)
                self.update_time_display(i, False)
                time.sleep(1)

            elapsed_time = time.time() - start_time

            if elapsed_time + small_break <= duration and self.is_running:
                self.play_sound(self.start_break_sound)
                self.status_label.config(text="休息中 ^_^")
                
                # 休息时间倒计时
                for i in range(int(small_break), 0, -1):
                    if not self.is_running:
                        return
                    remaining = duration - (time.time() - start_time)
                    if remaining > 0:
                        self.update_time_display(int(remaining), True)
                    time.sleep(1)
                
                self.play_sound(self.end_break_sound)

        if self.is_running:
            self.play_sound(self.major_cycle_end_sound)

    def run_break_cycle(self, duration):
        """运行休息周期"""
        self.current_cycle_type = "休息"
        start_time = time.time()
        self.status_label.config(text="休息中 ^_^")
        
        for i in range(int(duration), 0, -1):
            if not self.is_running:
                return
            self.update_time_display(i, True)
            time.sleep(1)

        if self.is_running:
            self.play_sound(self.major_cycle_end_sound)


def main():
    root = tk.Tk()
    app = TimeManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()