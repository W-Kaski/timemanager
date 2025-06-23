import time
import random
from playsound import playsound
import os

class TimeManager:
    def __init__(self):
        """
        Initialize the TimeManager with paths to sound files for different events.
        """
        self.sound_dir = "sounds"
        self.start_break_sound = os.path.join(self.sound_dir, "start_break.mp3")
        self.end_break_sound = os.path.join(self.sound_dir, "end_break.mp3")
        self.major_cycle_end_sound = os.path.join(self.sound_dir, "major_cycle_end.mp3")

    def play_sound(self, sound_file):
        """
        Play a sound file.

        Args:
            sound_file (str): Path to the sound file to be played.
        """
        try:
            playsound(sound_file)
        except Exception as e:
            print(f"播放声音时出错: {e}")

    def small_cycle(self, remaining_time):
        """
        Execute a small cycle during study time with random breaks.

        This method runs a loop until the remaining_time is exhausted. 
        It randomly generates study intervals between 4 to 6 minutes, 
        then plays a break sound and pauses for 10 seconds if time allows.

        Args:
            remaining_time (float): Total time in seconds for the small cycle.
        """
        start_time = time.time()
        elapsed_time = 0

        while elapsed_time < remaining_time:
            # 随机生成4-6分钟的学习时间
            study_time = random.randint(3, 10)
            # 确保不会超出大周期的剩余时间
            if elapsed_time + study_time > remaining_time:
                study_time = remaining_time - elapsed_time

            print(f"\n开始学习 {study_time/60:.2f} 分钟...")
            time.sleep(study_time)

            if elapsed_time + study_time + 10 <= remaining_time:
                # 播放休息开始提示音
                print("\n该休息了！")
                self.play_sound(self.start_break_sound)
                
                # 10秒休息时间
                time.sleep(10)
                
                # 播放休息结束提示音
                print("休息结束，继续学习！")
                self.play_sound(self.end_break_sound)

            elapsed_time = time.time() - start_time

    def major_cycle(self, cycles):
        """执行大周期"""
        for cycle in cycles:
            cycle_type = cycle["type"]
            duration = cycle["duration"] * 60  # 转换为秒

            print(f"\n开始 {cycle_type} 周期，持续 {cycle['duration']} 分钟")
            
            if cycle_type == "学习":
                self.small_cycle(duration)
            else:
                time.sleep(duration)

            # 播放大周期结束提示音
            print(f"\n{cycle_type}周期结束！")
            self.play_sound(self.major_cycle_end_sound)

def main():
    # 创建TimeManager实例
    manager = TimeManager()
    
    # 设置示例周期
    cycles = [
        {"type": "学习", "duration": 90},  # 90分钟学习
        {"type": "休息", "duration": 20},  # 20分钟休息
    ]

    try:
        while True:
            manager.major_cycle(cycles)
            user_input = input("\n按Enter继续下一轮循环，输入'q'退出：")
            if user_input.lower() == 'q':
                break
    except KeyboardInterrupt:
        print("\n程序已终止")

if __name__ == "__main__":
    main()


