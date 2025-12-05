import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk
import json
import os
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class StudyPlanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("2025计划管理V1.2")  # 更新版本号
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
        
        # 添加日期信息显示区域
        self.date_info_frame = tk.Frame(root, bg="#f6f8fa")
        self.date_info_frame.pack(side="bottom", fill="x", pady=(0, 8))
        
        self.create_date_label = tk.Label(self.date_info_frame, text="创建日期：", 
                                         font=("微软雅黑", 9), bg="#f6f8fa", fg="#666")
        self.create_date_label.pack(side="left", padx=10)
        
        self.last_punch_label = tk.Label(self.date_info_frame, text="最新打卡：", 
                                        font=("微软雅黑", 9), bg="#f6f8fa", fg="#666")
        self.last_punch_label.pack(side="left", padx=10)

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
                    # 为旧版本数据添加日期字段
                    for task in self.tasks:
                        if "create_date" not in task:
                            task["create_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        if "punch_dates" not in task:
                            task["punch_dates"] = []
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
            
        self.tasks.append({
            "name": task, 
            "done": False,
            "count": 0, 
            "target": target, 
            "description": description,
            "create_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "punch_dates": []
        })
        self.save_tasks()
        self.refresh_list()

    def punch_task(self):
        if self.selected_idx is not None:
            task = self.tasks[self.selected_idx]
            if not task["done"]:
                task["count"] += 1
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                task["punch_dates"].append(current_time)
                if task["count"] >= task["target"]:
                    task["done"] = True
                    messagebox.showinfo(
                        "恭喜", f"任务“{task['name']}”已达成目标，标记为完成！")
                self.save_tasks()
                self.refresh_list()
                self.update_date_display()

    def delete_task(self):
        if self.selected_idx is not None:
            del self.tasks[self.selected_idx]
            self.selected_idx = None
            self.save_tasks()
            self.refresh_list()
            self.update_date_display()

    def cancel_punch(self):
        """取消打卡：减少选中任务的打卡次数"""
        if self.selected_idx is not None:
            task = self.tasks[self.selected_idx]
            if task["count"] > 0:
                task["count"] -= 1
                if task["punch_dates"]:
                    task["punch_dates"].pop()
                # 如果取消后次数小于目标，且之前是完成状态，则取消完成状态
                if task["done"] and task["count"] < task["target"]:
                    task["done"] = False
                    messagebox.showinfo("提示", f"任务“{task['name']}”的完成状态已取消")
                self.save_tasks()
                self.refresh_list()
                self.update_date_display()
            else:
                messagebox.showwarning("警告", "打卡次数已经是0，无法再取消")
        else:
            messagebox.showwarning("警告", "请先选择一个任务")

    def update_date_display(self):
        """更新日期信息显示"""
        if self.selected_idx is not None:
            task = self.tasks[self.selected_idx]
            self.create_date_label.config(text=f"创建日期：{task['create_date']}")
            if task["punch_dates"]:
                last_punch = task["punch_dates"][-1]
                self.last_punch_label.config(text=f"最新打卡：{last_punch}")
            else:
                self.last_punch_label.config(text="最新打卡：暂无打卡记录")
        else:
            self.create_date_label.config(text="创建日期：")
            self.last_punch_label.config(text="最新打卡：")

    def show_task_detail(self, task_idx):
        task = self.tasks[task_idx]
        detail_win = tk.Toplevel(self.root)
        detail_win.title(f"任务详情 - {task['name']}")
        detail_win.geometry("480x450")  # 增加窗口宽度以适应滚动条
        detail_win.configure(bg="#f6f8fa")

        # 打卡日期列表 - 改为带滚动条的文本框
        tk.Label(detail_win, text="打卡日期列表：", font=("微软雅黑", 11, "bold"), bg="#f6f8fa", fg="#40916c").pack(anchor="w", padx=12, pady=(10, 2))
        
        # 创建框架容器
        date_frame = tk.Frame(detail_win, bg="#f6f8fa")
        date_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        
        # 创建滚动条
        scrollbar = tk.Scrollbar(date_frame)
        scrollbar.pack(side="right", fill="y")
        
        # 创建文本框显示打卡日期
        date_text = tk.Text(date_frame, 
                           height=6,  # 限定显示行数
                           width=50,  # 限定显示宽度
                           font=("微软雅黑", 10),
                           bg="#ffffff",
                           fg="#333",
                           wrap="word",  # 自动换行
                           yscrollcommand=scrollbar.set)
        date_text.pack(side="left", fill="both", expand=True)
        
        # 配置滚动条
        scrollbar.config(command=date_text.yview)
        
        # 插入打卡日期数据
        if task["punch_dates"]:
            date_text.insert("1.0", "\n".join(task["punch_dates"]))
        else:
            date_text.insert("1.0", "暂无打卡记录")
        
        # 设置文本框为只读
        date_text.config(state="disabled")

        # 图表展示 - 改为数轴显示
        if task["punch_dates"]:
            try:
                # 按时间顺序处理打卡数据
                from collections import defaultdict
                import matplotlib.dates as mdates
                from datetime import datetime
                
                # 按日期分组统计打卡次数
                date_count = defaultdict(int)
                time_points = []
                counts = []
                
                # 按时间顺序处理打卡记录
                sorted_dates = sorted(task["punch_dates"])
                for i, punch_time in enumerate(sorted_dates):
                    # 解析时间 - 修复格式匹配问题
                    dt = datetime.strptime(punch_time, "%Y-%m-%d %H:%M")
                    date_str = dt.strftime("%Y-%m-%d")
                    
                    # 统计当日打卡次数
                    date_count[date_str] += 1
                    
                    # 记录每个时间点的打卡次数
                    time_points.append(dt)
                    counts.append(date_count[date_str])
                
                # 创建图表
                fig = plt.Figure(figsize=(5, 3), dpi=100)
                ax = fig.add_subplot(111)
                
                # 绘制数轴图表（散点图+连线）
                ax.plot(time_points, counts, 'o-', color="#52b788", linewidth=2, markersize=6)
                
                # 设置图表标题和标签 - 更新X轴标签为"打卡日期"
                ax.set_title("打卡日期与次数趋势", fontsize=12, fontweight='bold', fontname='SimHei', pad=20)
                ax.set_xlabel("打卡日期", fontsize=10, fontname='SimHei')
                ax.set_ylabel("当日累计打卡次数", fontsize=10, fontname='SimHei')
                
                # 设置刻度标签字体 - 修改为正体显示
                for label in ax.get_xticklabels():
                    label.set_fontname('SimHei')
                    label.set_style('normal')  # 设置为正体，避免斜体显示
                for label in ax.get_yticklabels():
                    label.set_fontname('SimHei')
                    label.set_style('normal')  # 设置为正体，避免斜体显示
                
                # 格式化X轴日期显示 - 只显示日期，不显示时分
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                ax.tick_params(axis='x', rotation=0)  # 改为水平显示
                
                # 设置Y轴范围，从0开始，留出顶部空间避免标签重叠
                y_max = max(counts) if counts else 1
                ax.set_ylim(bottom=0, top=y_max * 1.2)  # 顶部留出20%空间
                
                # 添加网格线
                ax.grid(True, alpha=0.3)
                
                # 在数据点上添加标签显示打卡次数 - 调整位置避免重叠
                for i, (time_point, count) in enumerate(zip(time_points, counts)):
                    # 根据数据点位置动态调整标签位置
                    vertical_offset = 10  # 默认向上偏移
                    
                    # 如果数据点接近顶部，标签向下偏移
                    if count >= y_max * 0.8:
                        vertical_offset = -15
                    
                    ax.annotate(f'{count}', 
                               (time_point, count), 
                               textcoords="offset points", 
                               xytext=(0, vertical_offset), 
                               ha='center', 
                               fontsize=8,
                               color="#2d6a4f",
                               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
                
                # 调整布局，增加顶部边距
                fig.subplots_adjust(top=0.85)
                fig.tight_layout()
                
                canvas = FigureCanvasTkAgg(fig, master=detail_win)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=8)
                
            except Exception as e:
                tk.Label(detail_win, text=f"图表显示失败：{e}", fg="red", bg="#f6f8fa").pack(pady=8)
        else:
            tk.Label(detail_win, text="暂无打卡数据，无法生成图表", fg="#aaa", bg="#f6f8fa").pack(pady=8)

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
            
            # 问号备注框
            question_label = tk.Label(right_frame, text="❓", font=("微软雅黑", 10),
                                     bg="#ffffff", fg="#666", cursor="hand2")
            question_label.pack(side="left", padx=2)
            
            # 详情框
            detail_label = tk.Label(right_frame, text="📊", font=("微软雅黑", 11),
                                   bg="#ffffff", fg="#40916c", cursor="hand2")
            detail_label.pack(side="left", padx=2)

            # 备注提示框
            if t.get("description"):
                def create_tooltip_for_task(task_description):
                    tooltip = tk.Toplevel(self.root)
                    tooltip.withdraw()
                    tooltip.overrideredirect(True)
                    tooltip.configure(bg="#ffffe0", relief="solid", bd=1)
                    tooltip_label = tk.Label(tooltip, text=task_description, 
                                            font=("微软雅黑", 9), bg="#ffffe0", 
                                            fg="#333", justify="left", wraplength=200)
                    tooltip_label.pack(padx=5, pady=3)
                    return tooltip
                tooltip = create_tooltip_for_task(t["description"])
                def show_tooltip(event, tooltip=tooltip):
                    tooltip.deiconify()
                    tooltip.geometry(f"+{event.x_root+10}+{event.y_root+10}")
                def hide_tooltip(event, tooltip=tooltip):
                    tooltip.withdraw()
                question_label.bind("<Enter>", show_tooltip)
                question_label.bind("<Leave>", hide_tooltip)
                question_label.bind("<Motion>", show_tooltip)
            
            # 编辑备注
            def edit_description(event, task_idx=idx):
                current_description = self.tasks[task_idx].get("description", "")
                new_description = simpledialog.askstring("编辑备注", 
                                                       "请输入任务备注：", 
                                                       initialvalue=current_description)
                if new_description is not None:
                    self.tasks[task_idx]["description"] = new_description
                    self.save_tasks()
                    self.refresh_list()
            question_label.bind("<Button-1>", edit_description)

            # 详情弹窗（修改为同时处理选中效果和弹出窗口）
            def handle_detail_click(event, task_idx=idx):
                # 先选中任务
                self.selected_idx = task_idx
                self.refresh_list()
                self.update_date_display()
                # 然后弹出详情窗口
                self.show_task_detail(task_idx)
            detail_label.bind("<Button-1>", handle_detail_click)

            # 选中效果（其他元素保持不变）
            def select_row(event, idx=idx):
                self.selected_idx = idx
                self.refresh_list()
                self.update_date_display()
            row.bind("<Button-1>", select_row)
            label.bind("<Button-1>", select_row)
            bar.bind("<Button-1>", select_row)
            percent_label.bind("<Button-1>", select_row)
            # 删除这一行：detail_label.bind("<Button-1>", select_row)
            if self.selected_idx == idx:
                row.config(bg="#e0ffe0")
                label.config(bg="#e0ffe0")
                percent_label.config(bg="#e0ffe0")
                question_label.config(bg="#e0ffe0")
                detail_label.config(bg="#e0ffe0")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("470x500")  # 增加窗口高度以容纳日期信息
    #  # 设置窗口图标
    # try:
    #     icon_path = os.path.join(os.path.dirname(__file__), 'study_icon.ico')
    #     if os.path.exists(icon_path):
    #         root.iconbitmap(icon_path)
    # except Exception as e:
    #     print(f"设置图标时出错: {e}")
    app = StudyPlanApp(root)
    root.mainloop()

# pyinstaller -F -w ./src/plan.py --distpath ./output/dist --workpath ./output/build

# 配置matplotlib中文字体支持
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']  # 设置中文字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题