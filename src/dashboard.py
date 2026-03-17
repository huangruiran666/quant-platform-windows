"""
Main module for dashboard.py.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
import threading
from datetime import datetime
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class OmniHoloCockpit:
    def __init__(self, root):
        self.root = root
        self.root.title("🌌 奇点：全息主宰指挥舱 v23.1 [ULTRA STABLE]")
        self.root.geometry("1750x1050")
        self.root.configure(bg="#010205")
        
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        self.root.geometry(f"1750x1050+{int((sw-1750)/2)}+{int((sh-1050)/2)}")

        self.full_stocks = pd.DataFrame()
        self.setup_styles()
        self.create_header()
        self.create_tabs()
        self.root.after(500, self.async_sync_all)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#010205", borderwidth=0)
        style.configure("TNotebook.Tab", background="#0d1117", foreground="#8b949e", font=("微软雅黑", 12), padding=[20, 5])
        style.map("TNotebook.Tab", background=[("selected", "#1a1f26")], foreground=[("selected", "#58a6ff")])
        style.configure("Treeview", background="#02060a", foreground="#00ff00", fieldbackground="#02060a", rowheight=40)
        style.configure("Treeview.Heading", background="#0d1117", foreground="#ffffff", font=("微软雅黑", 11, "bold"))

    def create_header(self):
        header = tk.Frame(self.root, bg="#050a0f", pady=25, bd=1, relief=tk.SOLID)
        header.pack(fill=tk.X)
        tk.Label(header, text="🌌 SINGULARITY SOVEREIGN", font=("Consolas", 28, "bold"), bg="#050a0f", fg="#58a6ff").pack(side=tk.LEFT, padx=40)
        
        self.decision_frame = tk.Frame(header, bg="#1a1a1a", padx=40, pady=5, bd=2, relief=tk.RIDGE)
        self.decision_frame.pack(side=tk.RIGHT, padx=60)
        tk.Label(self.decision_frame, text="主宰级最终决议", font=("微软雅黑", 10), bg="#1a1a1a", fg="#888888").pack()
        self.action_label = tk.Label(self.decision_frame, text="等待激活", font=("微软雅黑", 24, "bold"), bg="#1a1a1a", fg="#ffffff")
        self.action_label.pack()

        self.macro_bar = tk.Label(header, text="🌍 全球感知: 同步中...", font=("Consolas", 12), bg="#050a0f", fg="#39ff14")
        self.macro_bar.pack(side=tk.RIGHT, padx=20)

    def create_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.tab_sniper = tk.Frame(self.notebook, bg="#010205")
        self.notebook.add(self.tab_sniper, text=" 🎯 定向狙击 ")
        self.setup_sniper_tab()

        self.tab_sectors = tk.Frame(self.notebook, bg="#010205")
        self.notebook.add(self.tab_sectors, text=" 🔥 板块热力 ")
        self.sector_box = scrolledtext.ScrolledText(self.tab_sectors, bg="#000000", fg="#ff4500", font=("Consolas", 14))
        self.sector_box.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)

        self.tab_radar = tk.Frame(self.notebook, bg="#010205")
        self.notebook.add(self.tab_radar, text=" 📡 雷达扫描 ")
        self.setup_radar_tab()

        self.tab_single = tk.Frame(self.notebook, bg="#010205")
        self.notebook.add(self.tab_single, text=" 🔬 单股深析 ")
        self.setup_single_stock_tab()

    def setup_sniper_tab(self):
        pane = tk.PanedWindow(self.tab_sniper, orient=tk.HORIZONTAL, bg="#010205", bd=0, sashwidth=8)
        pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        left = tk.Frame(pane, bg="#050a0f")
        pane.add(left, width=600)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_data())
        tk.Entry(left, textvariable=self.search_var, font=("微软雅黑", 14), bg="#000000", fg="#39ff14").pack(fill=tk.X, padx=10, pady=10)

        self.tree = ttk.Treeview(left, columns=("名称", "代码", "动能分"), show='headings')
        for c in ("名称", "代码", "动能分"): self.tree.heading(c, text=c); self.tree.column(c, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)

        right = tk.Frame(pane, bg="#050a0f")
        pane.add(right)
        self.report_box = scrolledtext.ScrolledText(right, bg="#000000", fg="#ffffff", font=("微软雅黑", 13), wrap=tk.WORD)
        self.report_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.fire_btn = tk.Button(right, text="🔥 激活最高投委会博弈序列", command=self.fire_audit, bg="#d73a49", fg="white", font=("微软雅黑", 16, "bold"), height=3)
        self.fire_btn.pack(fill=tk.X, pady=10)

    def async_sync_all(self):
        def task():
            try:
                from data_engine import FullSovereignEngine
                stocks, sectors, macro, vitals = FullSovereignEngine.get_omni_data()
                self.full_stocks = stocks
                self.root.after(0, lambda: self.refresh_ui(stocks, sectors, macro, vitals))
            except: pass
        threading.Thread(target=task, daemon=True).start()

    def refresh_ui(self, stocks, sectors, macro, vitals):
        self.macro_bar.config(text=f"🌍 USD/CNH: {macro.get('USD_CNH')} | A50: {macro.get('A50_FUT')}")
        self.update_list(stocks)
        self.sector_box.insert(tk.END, f"\n[新同步时间: {datetime.now().strftime('%H:%M:%S')}]\n" + "\n".join([f"● {s['名称']} ({s['涨跌幅']}%)" for s in sectors]))

    def update_list(self, df):
        for i in self.tree.get_children(): self.tree.delete(i)
        if df.empty: return
        # 核心防御：列名检查
        cols = df.columns
        for _, r in df.head(100).iterrows():
            name = r.get('名称', 'N/A')
            code = r.get('代码', 'N/A')
            score = r.get('CORE_SCORE', 0)
            self.tree.insert("", tk.END, values=(name, code, f"{score:.2f}"))

    def filter_data(self):
        if self.full_stocks.empty: return
        val = self.search_var.get().strip().lower()
        df = self.full_stocks
        mask = df.get('名称', pd.Series()).astype(str).str.contains(val, na=False) | \
               df.get('代码', pd.Series()).astype(str).str.contains(val, na=False)
        self.update_list(df[mask])

    def fire_audit(self):
        sel = self.tree.selection()
        name = self.tree.item(sel[0])['values'][0] if sel else ""
        self.fire_btn.config(state=tk.DISABLED, text="🚀 正在调动全球算力...")
        def run():
            from quant_master import SingularityMassiveCore
            result = SingularityMassiveCore().run_surgical_audit(name)
            self.root.after(0, lambda: self.on_audit_finish(result))
        threading.Thread(target=run, daemon=True).start()

    def on_audit_finish(self, result: dict):
        self.fire_btn.config(state=tk.NORMAL, text="🔥 激活最高投委会博弈序列")
        if result:
            self.action_label.config(text=result.get('action', '观察'), fg="#ff4500")
            self.report_box.delete("1.0", tk.END)
            self.report_box.insert(tk.END, result.get('report', ''))

    # ── 雷达扫描 Tab ──────────────────────────────────────────────
    def setup_radar_tab(self):
        top = tk.Frame(self.tab_radar, bg="#010205")
        top.pack(fill=tk.X, padx=10, pady=10)
        self.radar_btn = tk.Button(
            top, text="🔍 启动全市场雷达扫描",
            command=self.fire_radar, bg="#1a4a1a", fg="#39ff14",
            font=("微软雅黑", 14, "bold"), height=2,
        )
        self.radar_btn.pack(fill=tk.X)

        pane = tk.PanedWindow(self.tab_radar, orient=tk.HORIZONTAL, bg="#010205", sashwidth=8)
        pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        left = tk.Frame(pane, bg="#050a0f")
        pane.add(left, width=700)
        self.radar_tree = ttk.Treeview(left, columns=("代码", "名称", "涨跌幅", "换手率", "成交额"), show="headings")
        for c in ("代码", "名称", "涨跌幅", "换手率", "成交额"):
            self.radar_tree.heading(c, text=c)
            self.radar_tree.column(c, anchor=tk.CENTER, width=130)
        self.radar_tree.pack(fill=tk.BOTH, expand=True)

        right = tk.Frame(pane, bg="#050a0f")
        pane.add(right)
        self.radar_report = scrolledtext.ScrolledText(right, bg="#000000", fg="#39ff14", font=("微软雅黑", 13), wrap=tk.WORD)
        self.radar_report.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def fire_radar(self):
        self.radar_btn.config(state=tk.DISABLED, text="📡 扫描中...")
        def run():
            from radar import get_market_radar, ai_portfolio_evaluator
            candidates = get_market_radar()
            report = ai_portfolio_evaluator(candidates) if not candidates.empty else "未找到符合条件的标的"
            self.root.after(0, lambda: self.on_radar_finish(candidates, report))
        threading.Thread(target=run, daemon=True).start()

    def on_radar_finish(self, df: pd.DataFrame, report: str):
        self.radar_btn.config(state=tk.NORMAL, text="🔍 启动全市场雷达扫描")
        for i in self.radar_tree.get_children():
            self.radar_tree.delete(i)
        if not df.empty:
            for _, r in df.iterrows():
                self.radar_tree.insert("", tk.END, values=(
                    r.get("代码", ""), r.get("名称", ""),
                    f"{r.get('涨跌幅', 0):.2f}%", f"{r.get('换手率', 0):.2f}%",
                    f"{r.get('成交额', 0)/1e8:.2f}亿",
                ))
        self.radar_report.delete("1.0", tk.END)
        self.radar_report.insert(tk.END, report)

    # ── 单股深析 Tab ──────────────────────────────────────────────
    def setup_single_stock_tab(self):
        top = tk.Frame(self.tab_single, bg="#010205")
        top.pack(fill=tk.X, padx=20, pady=15)
        tk.Label(top, text="股票代码:", font=("微软雅黑", 14), bg="#010205", fg="#8b949e").pack(side=tk.LEFT)
        self.single_code_var = tk.StringVar(value="600519")
        tk.Entry(top, textvariable=self.single_code_var, font=("微软雅黑", 14), bg="#000000",
                 fg="#39ff14", width=12).pack(side=tk.LEFT, padx=10)
        self.single_btn = tk.Button(
            top, text="🔬 深度解析", command=self.fire_single,
            bg="#1a2a4a", fg="#58a6ff", font=("微软雅黑", 14, "bold"),
        )
        self.single_btn.pack(side=tk.LEFT)

        self.single_report = scrolledtext.ScrolledText(
            self.tab_single, bg="#000000", fg="#ffffff", font=("微软雅黑", 13), wrap=tk.WORD,
        )
        self.single_report.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def fire_single(self):
        code = self.single_code_var.get().strip()
        if not code:
            return
        self.single_btn.config(state=tk.DISABLED, text="⏳ 分析中...")
        def run():
            from a_share_quant import get_a_share_data, ai_expert_decision
            try:
                data = get_a_share_data(code)
                report = ai_expert_decision(code, data)
            except Exception as e:
                report = f"分析失败: {e}"
            self.root.after(0, lambda: self.on_single_finish(report))
        threading.Thread(target=run, daemon=True).start()

    def on_single_finish(self, report: str):
        self.single_btn.config(state=tk.NORMAL, text="🔬 深度解析")
        self.single_report.delete("1.0", tk.END)
        self.single_report.insert(tk.END, report)

if __name__ == "__main__":
    root = tk.Tk()
    app = OmniHoloCockpit(root)
    root.mainloop()
