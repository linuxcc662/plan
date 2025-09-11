import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk
import json
import os


class StudyPlanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("2025计划管理V1.1")
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
        tk.Button(btn_frame, text="取消打卡", command=self.cancel_punch,
                  **btn_style).pack(side="left", padx=8)
        tk.Button(btn_frame, text="删除任务", command=self.delete_task,
                  **btn_style).pack(side="left", padx=8)

        self.selected_idx = None
        self.load_tasks()
        self.refresh_list()

        footer = tk.Label(root, text="© 2025 linuxcc", font=(
            "微软雅黑", 9), bg="#f6f8fa", fg="#aaa")
        footer.pack(side="bottom", pady=8)

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
        
        # 新增备注输入
        description = simpledialog.askstring("任务备注", "请输入任务备注（可选）：")
        if description is None:  # 用户点击取消
            description = ""
            
        self.tasks.append({"name": task, "done": False,
                          "count": 0, "target": target, "description": description})
        self.save_tasks()
        self.refresh_list()

    def punch_task(self):
        if self.selected_idx is not None:
            task = self.tasks[self.selected_idx]
            if not task["done"]:
                task["count"] += 1
                if task["count"] >= task["target"]:
                    task["done"] = True
                    messagebox.showinfo(
                        "恭喜", f"任务“{task['name']}”已达成目标，标记为完成！")
                self.save_tasks()
                self.refresh_list()

    def delete_task(self):
        if self.selected_idx is not None:
            del self.tasks[self.selected_idx]
            self.selected_idx = None
            self.save_tasks()
            self.refresh_list()

    def cancel_punch(self):
        """取消打卡：减少选中任务的打卡次数"""
        if self.selected_idx is not None:
            task = self.tasks[self.selected_idx]
            if task["count"] > 0:
                task["count"] -= 1
                # 如果取消后次数小于目标，且之前是完成状态，则取消完成状态
                if task["done"] and task["count"] < task["target"]:
                    task["done"] = False
                    messagebox.showinfo("提示", f"任务“{task['name']}”的完成状态已取消")
                self.save_tasks()
                self.refresh_list()
            else:
                messagebox.showwarning("警告", "打卡次数已经是0，无法再取消")
        else:
            messagebox.showwarning("警告", "请先选择一个任务")

    def refresh_list(self):
        for widget in self.task_frame.winfo_children():
            widget.destroy()
        for idx, t in enumerate(self.tasks):
            row = tk.Frame(self.task_frame, bg="#ffffff",
                           highlightbackground="#e0e0e0", highlightthickness=1)
            row.pack(fill="x", pady=5, padx=10, ipadx=4, ipady=3)
            
            # 左侧任务信息
            left_frame = tk.Frame(row, bg="#ffffff")
            left_frame.pack(side="left", fill="both", expand=True)
            
            status = "✔️" if t["done"] else "❌"
            percent = int((t["count"] / t["target"]) *
                          100) if t["target"] > 0 else 0
            txt = f"{status} {t['name']} [{t['count']}/{t['target']}]"
            label = tk.Label(left_frame, text=txt, font=("微软雅黑", 12),
                             anchor="w", bg="#ffffff", fg="#333")
            label.pack(fill="x", padx=2)
            
            # 右侧进度条和问号框
            right_frame = tk.Frame(row, bg="#ffffff")
            right_frame.pack(side="right", padx=5)
            
            bar = ttk.Progressbar(right_frame, length=80, mode="determinate")
            bar["value"] = percent
            bar.pack(side="left", padx=2)
            
            percent_label = tk.Label(right_frame, text=f"{percent}%", font=(
                "微软雅黑", 11), bg="#ffffff", fg="#40916c")
            percent_label.pack(side="left", padx=2)
            
            # 为所有任务添加问号框（无论是否有备注）
            question_label = tk.Label(right_frame, text="❓", font=("微软雅黑", 10),
                                     bg="#ffffff", fg="#666", cursor="hand2")
            question_label.pack(side="left", padx=2)
            
            # 为每个任务创建独立的提示框（如果有备注）
            if t.get("description"):
                def create_tooltip_for_task(task_description):
                    tooltip = tk.Toplevel(self.root)
                    tooltip.withdraw()  # 初始隐藏
                    tooltip.overrideredirect(True)  # 去除窗口装饰
                    tooltip.configure(bg="#ffffe0", relief="solid", bd=1)
                    
                    tooltip_label = tk.Label(tooltip, text=task_description, 
                                            font=("微软雅黑", 9), bg="#ffffe0", 
                                            fg="#333", justify="left", wraplength=200)
                    tooltip_label.pack(padx=5, pady=3)
                    return tooltip
                
                # 为当前任务创建提示框
                tooltip = create_tooltip_for_task(t["description"])
                
                # 鼠标悬停事件（仅对有备注的任务）
                def show_tooltip(event, tooltip=tooltip):
                    tooltip.deiconify()
                    tooltip.geometry(f"+{event.x_root+10}+{event.y_root+10}")
                
                def hide_tooltip(event, tooltip=tooltip):
                    tooltip.withdraw()
                
                question_label.bind("<Enter>", show_tooltip)
                question_label.bind("<Leave>", hide_tooltip)
                question_label.bind("<Motion>", show_tooltip)
            
            # 点击编辑事件（对所有任务有效）
            def edit_description(event, task_idx=idx):
                current_description = self.tasks[task_idx].get("description", "")
                new_description = simpledialog.askstring("编辑备注", 
                                                       "请输入任务备注：", 
                                                       initialvalue=current_description)
                if new_description is not None:  # 用户点击确定
                    self.tasks[task_idx]["description"] = new_description
                    self.save_tasks()
                    self.refresh_list()  # 刷新列表以更新显示
            
            question_label.bind("<Button-1>", edit_description)  # 添加点击事件
            
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
                question_label.config(bg="#e0ffe0")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("470x480")
    app = StudyPlanApp(root)
    root.mainloop()