import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk
import json
import os

class StudyPlanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("2025计划管理")
        self.tasks = []
        self.data_file = "study_tasks.json"

        self.root.configure(bg="#f6faf6")  # 设置主窗口背景色

        title = tk.Label(root, text="学习进度管理", font=(
            "微软雅黑", 22, "bold"), bg="#f6f8fa", fg="#2d6a4f")
        title.pack(pady=(18, 6))

        self.task_frame = tk.Frame(root, bg="#f6f8fa")
        self.task_frame.pack(pady=10)

        btn_frame = tk.Frame(root, bg="#f6f8fa")
        btn_frame.pack(pady=10)

        btn_style = {
            "font": ("微软雅黑", 12, "bold"),
            "bg": "#40916c",
            "fg": "white",
            "activebackground": "#52b788",
            "activeforeground": "white",
            "bd": 0,
            "relief": "ridge",
            "width": 10,
            "height": 1,
            "cursor": "hand2"
        }
        tk.Button(btn_frame, text="添加任务", command=self.add_task,
                  **btn_style).pack(side="left", padx=8)
        tk.Button(btn_frame, text="打卡", command=self.punch_task,
                  **btn_style).pack(side="left", padx=8)
        tk.Button(btn_frame, text="删除任务", command=self.delete_task,
                  **btn_style).pack(side="left", padx=8)

        self.selected_idx = None
        self.load_tasks()
        self.refresh_list()

        footer = tk.Label(root, text="© 2025 linuxcc", font=(
            "微软雅黑", 9), bg="#f6f8fa", fg="#aaa")
        footer.pack(side="bottom", pady=8)

    # def setup_webdav(self):
    #     options = {
    #         'webdav_hostname': "https://dav.jianguoyun.com/dav/",
    #         'webdav_login':    "854456080@qq.com",
    #         'webdav_password': "a5eyixhv7czw6acc"
    #     }
    #     self.webdav_client = Client(options)

    # def setup_webdav(self):
    #     try:
    #         options = {
    #             'webdav_hostname': "https://dav.jianguoyun.com/dav/",
    #             'webdav_login':"854456080@qq.com",
    #             'webdav_password': "a5eyixhv7czw6acc",
    #             'webdav_timeout': 30  # 增加超时设置
    #         }
    #         self.webdav_client = Client(options)
    #         # 测试连接
    #         self.webdav_client.list()
    #         print("WebDAV连接成功")
    #     except Exception as e:
    #         messagebox.showerror("WebDAV配置错误", f"初始化WebDAV客户端失败：{e}")
    #         self.webdav_client = None
    # # 上传本地文件到坚果云WebDAV
    # def upload_json_to_webdav(self):
    #     if not self.webdav_client:
    #         messagebox.showwarning("WebDAV未初始化", "无法执行同步操作，请检查网络连接和账号配置")
    #         return
        
    #     try:
    #         # 确保远程目录存在
    #         if not self.webdav_client.check(remote_path="dav/plan/"):
    #             self.webdav_client.mkdir(remote_path="dav/plan/")
    #             print("WebDAV目录创建成功或已存在")
    #         self.webdav_client.upload_sync(remote_path="dav/plan/study_tasks.json", local_path=self.data_file)
    #         messagebox.showinfo("WebDAV同步", "任务已成功同步到云端！")
    #     except Exception as e:
    #         messagebox.showerror("WebDAV上传失败", f"同步到WebDAV时出错：{e}\n\n可能原因：\n1. 网络连接问题\n2. 坚果云账号信息变更\n3. 远程目录权限问题")  
    # def download_json_from_webdav(self):
    #     if not self.webdav_client:
    #         return
            
    #     try:
    #         self.webdav_client.download_sync(remote_path="dav/plan/study_tasks.json", local_path=self.data_file)
    #     except Exception as e:
    #         # 下载失败时不弹出错误，避免影响程序运行
    #         print(f"WebDAV下载失败: {e}")
    #  def upload_json_to_webdav(self):
    #     try:
    #         self.webdav_client.upload_sync(remote_path="dav/plan/study_tasks.json", local_path=self.data_file)
    #         messagebox.showinfo("WebDAV同步", "任务已成功同步到云端！")
    #     except Exception as e:
    #         messagebox.showerror("WebDAV上传失败", f"同步到WebDAV时出错：{e}")

    # def download_json_from_webdav(self):
    #     try:
    #         self.webdav_client.download_sync(remote_path="dav/plan/study_tasks.json", local_path=self.data_file)
    #     except Exception as e:
    #         messagebox.showerror("WebDAV下载失败", f"从WebDAV同步时出错：{e}")

    def save_tasks(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("保存失败", f"保存任务时出错：{e}")
        # self.upload_json_to_webdav()

    def load_tasks(self):
        # self.setup_webdav()
        # self.download_json_from_webdav()
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
            except Exception as e:
                messagebox.showerror("加载失败", f"加载任务时出错：{e}")
                self.tasks = []

    def add_task(self):
        task = simpledialog.askstring("添加任务", "请输入学习任务：")
        if not task:
            return
        try:
            target = int(simpledialog.askstring("目标次数", "请输入目标打卡次数："))
        except (TypeError, ValueError):
            messagebox.showerror("错误", "目标次数必须为整数！")
            return
        self.tasks.append({"name": task, "done": False, "count": 0, "target": target})
        self.save_tasks()
        self.refresh_list()

    def punch_task(self):
        if self.selected_idx is not None:
            task = self.tasks[self.selected_idx]
            if not task["done"]:
                task["count"] += 1
                if task["count"] >= task["target"]:
                    task["done"] = True
                    messagebox.showinfo("恭喜", f"任务“{task['name']}”已达成目标，标记为完成！")
                self.save_tasks()
                self.refresh_list()

    def delete_task(self):
        if self.selected_idx is not None:
            del self.tasks[self.selected_idx]
            self.selected_idx = None
            self.save_tasks()
            self.refresh_list()

    def refresh_list(self):
        for widget in self.task_frame.winfo_children():
            widget.destroy()
        for idx, t in enumerate(self.tasks):
            row = tk.Frame(self.task_frame, bg="#ffffff", highlightbackground="#e0e0e0", highlightthickness=1)
            row.pack(fill="x", pady=5, padx=10, ipadx=4, ipady=3)
            status = "✔️" if t["done"] else "❌"
            percent = int((t["count"] / t["target"]) * 100) if t["target"] > 0 else 0
            txt = f"{status} {t['name']} [{t['count']}/{t['target']}]"
            label = tk.Label(row, text=txt, font=("微软雅黑", 12), anchor="w", width=22, bg="#ffffff", fg="#333")
            label.pack(side="left", padx=2)
            bar = ttk.Progressbar(row, length=80, mode="determinate")
            bar["value"] = percent
            bar.pack(side="left", padx=5)
            percent_label = tk.Label(row, text=f"{percent}%", font=("微软雅黑", 11), width=5, bg="#ffffff", fg="#40916c")
            percent_label.pack(side="left", padx=2)
            # 选中效果
            def select_row(event, idx=idx):
                self.selected_idx = idx
                self.refresh_list()
            row.bind("<Button-1>", select_row)
            label.bind("<Button-1>", select_row)
            bar.bind("<Button-1>", select_row)
            percent_label.bind("<Button-1>", select_row)
            if self.selected_idx == idx:
                row.config(bg="#e0ffe0")
                label.config(bg="#e0ffe0")
                percent_label.config(bg="#e0ffe0")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("470x480")
    app = StudyPlanApp(root)
    root.mainloop()