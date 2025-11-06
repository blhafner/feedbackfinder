import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import requests
import json
import threading
import queue
import time
import csv
from datetime import datetime, timedelta
from calendar import monthrange
from deep_translator import GoogleTranslator
import openai

class DatePicker:
    """Modern airline-style date picker widget"""
    def __init__(self, parent, initial_date=None, callback=None):
        self.parent = parent
        self.callback = callback
        self.selected_date = initial_date or datetime.now()
        
        # Create button frame
        self.frame = tk.Frame(parent, bg=parent.cget('bg'))
        self.button = tk.Button(self.frame, 
                               text=self.selected_date.strftime("%b %d, %Y"),
                               font=("Segoe UI", 11, "bold"),
                               bg='white',
                               fg='#000000',
                               activebackground='#f0f0f0',
                               activeforeground='#000000',
                               relief='solid',
                               borderwidth=1,
                               padx=12,
                               pady=8,
                               cursor='hand2',
                               command=self.show_calendar)
        self.button.pack()
        
    def show_calendar(self):
        """Show calendar popup"""
        # Create popup window
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("Select Date")
        self.popup.geometry("320x380")
        self.popup.configure(bg='#ffffff')
        self.popup.resizable(False, False)
        self.popup.transient(self.parent)
        self.popup.grab_set()
        
        # Center the popup
        self.popup.update_idletasks()
        x = (self.popup.winfo_screenwidth() // 2) - (320 // 2)
        y = (self.popup.winfo_screenheight() // 2) - (380 // 2)
        self.popup.geometry(f"320x380+{x}+{y}")
        
        # Header with month/year navigation
        header = tk.Frame(self.popup, bg='#005482', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Previous month button
        prev_btn = tk.Button(header, text="◀", font=("Segoe UI", 14, "bold"),
                           bg='#005482', fg='white', activebackground='#006ba3',
                           activeforeground='white', relief='flat', borderwidth=0,
                           width=3, command=lambda: self.change_month(-1))
        prev_btn.pack(side='left', padx=10)
        
        # Month/Year label
        self.month_label = tk.Label(header, 
                                    text=self.selected_date.strftime("%B %Y"),
                                    font=("Segoe UI", 16, "bold"),
                                    bg='#005482', fg='white')
        self.month_label.pack(side='left', expand=True)
        
        # Next month button
        next_btn = tk.Button(header, text="▶", font=("Segoe UI", 14, "bold"),
                           bg='#005482', fg='white', activebackground='#006ba3',
                           activeforeground='white', relief='flat', borderwidth=0,
                           width=3, command=lambda: self.change_month(1))
        next_btn.pack(side='right', padx=10)
        
        # Day names header
        days_frame = tk.Frame(self.popup, bg='#ffffff')
        days_frame.pack(fill='x', padx=10, pady=(10, 0))
        day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        for day in day_names:
            label = tk.Label(days_frame, text=day, font=("Segoe UI", 10, "bold"),
                           bg='#ffffff', fg='#666666', width=4)
            label.pack(side='left', expand=True)
        
        # Calendar grid
        self.calendar_frame = tk.Frame(self.popup, bg='#ffffff')
        self.calendar_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.draw_calendar()
        
        # Today button
        today_btn = tk.Button(self.popup, text="Today", 
                            font=("Segoe UI", 10, "bold"),
                            bg='#005482', fg='white',
                            activebackground='#006ba3',
                            activeforeground='white',
                            relief='flat', borderwidth=0,
                            padx=20, pady=8,
                            command=self.select_today)
        today_btn.pack(pady=(0, 10))
    
    def draw_calendar(self):
        """Draw calendar grid"""
        # Clear existing buttons
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        year = self.selected_date.year
        month = self.selected_date.month
        
        # Get first day of month and number of days
        first_day, num_days = monthrange(year, month)
        first_day = (first_day + 1) % 7  # Convert to Sunday=0 format
        
        # Create calendar grid
        row = 0
        col = 0
        
        # Empty cells for days before month starts
        for _ in range(first_day):
            cell = tk.Frame(self.calendar_frame, bg='#ffffff', width=40, height=40)
            cell.grid(row=row, column=col, padx=2, pady=2)
            col += 1
        
        # Days of the month
        today = datetime.now()
        for day in range(1, num_days + 1):
            date_obj = datetime(year, month, day)
            is_today = (date_obj.date() == today.date())
            is_selected = (date_obj.date() == self.selected_date.date())
            
            # Determine cell color
            if is_selected:
                bg_color = '#005482'
                fg_color = 'white'
            elif is_today:
                bg_color = '#e0f0ea'
                fg_color = '#000000'
            else:
                bg_color = 'white'
                fg_color = '#000000'
            
            btn = tk.Button(self.calendar_frame, text=str(day),
                          font=("Segoe UI", 11, "bold" if is_selected else "normal"),
                          bg=bg_color, fg=fg_color,
                          activebackground='#006ba3' if not is_selected else '#005482',
                          activeforeground='white',
                          relief='solid', borderwidth=1,
                          width=4, height=2,
                          cursor='hand2',
                          command=lambda d=day: self.select_date(year, month, d))
            btn.grid(row=row, column=col, padx=2, pady=2)
            
            col += 1
            if col > 6:
                col = 0
                row += 1
    
    def change_month(self, delta):
        """Change displayed month"""
        if delta == -1:
            # Previous month
            if self.selected_date.month == 1:
                self.selected_date = self.selected_date.replace(year=self.selected_date.year - 1, month=12)
            else:
                self.selected_date = self.selected_date.replace(month=self.selected_date.month - 1)
        else:
            # Next month
            if self.selected_date.month == 12:
                self.selected_date = self.selected_date.replace(year=self.selected_date.year + 1, month=1)
            else:
                self.selected_date = self.selected_date.replace(month=self.selected_date.month + 1)
        
        self.month_label.config(text=self.selected_date.strftime("%B %Y"))
        self.draw_calendar()
    
    def select_date(self, year, month, day):
        """Select a date"""
        self.selected_date = datetime(year, month, day)
        self.button.config(text=self.selected_date.strftime("%b %d, %Y"))
        self.popup.destroy()
        if self.callback:
            self.callback(self.selected_date)
    
    def select_today(self):
        """Select today's date"""
        self.selected_date = datetime.now()
        self.button.config(text=self.selected_date.strftime("%b %d, %Y"))
        self.popup.destroy()
        if self.callback:
            self.callback(self.selected_date)
    
    def get_date(self):
        """Get selected date as string in YYYY-MM-DD format"""
        return self.selected_date.strftime("%Y-%m-%d")
    
    def set_date(self, date_str):
        """Set date from YYYY-MM-DD string"""
        try:
            self.selected_date = datetime.strptime(date_str, "%Y-%m-%d")
            self.button.config(text=self.selected_date.strftime("%b %d, %Y"))
        except ValueError:
            pass
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

class ModernIntercomApp:
    def __init__(self, root):
        self.root = root
        self.root.title("fdbckfndr v1.0")
        self.root.geometry("900x850")
        
        # Modern color scheme
        self.colors = {
            'bg': '#e0f0ea',
            'card': '#95adbe',
            'primary': '#005482',
            'success': '#008c52',
            'warning': '#d97706',
            'danger': '#ef4444',
            'text': '#000000',  # Pure black for maximum contrast
            'text_secondary': '#000000',  # Pure black for maximum contrast
            'border': '#574f7d'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Configure modern style
        style = ttk.Style()
        style.theme_use('aqua')
        style.configure("Modern.Horizontal.TProgressbar", 
                       troughcolor=self.colors['border'],
                       background=self.colors['primary'],
                       bordercolor=self.colors['border'],
                       relief='flat')
        
        # Internal State
        self.log_queue = queue.Queue()
        self.final_report_data = []
        self.admin_map = {}
        self.team_map = {}
        self.team_admins_map = {}  # Maps team_id to list of admin_ids
        self.total_conversations = 0
        self.total_pages = 0
        self.total_found = 0
        self.time_per_page = 0
        self.start_time = 0
        self.ai_insights = {}
        self.translations_cache = {}
        self.translator = GoogleTranslator(source='auto', target='en')
        self.openai_api_key = ""  # Set your OpenAI API key here or load from config
        
        self.setup_button_styles()
        self.create_ui()
        self.root.after(100, self.process_queue)
        self.root.after(100, self.animate_loading)
    
    def setup_button_styles(self):
        """Configure button styles for better readability"""
        style = ttk.Style()
        # Configure button styles with high contrast
        style.configure("Primary.TButton",
                       background=self.colors['primary'],
                       foreground='#000000',
                       borderwidth=0,
                       focuscolor='none',
                       padding=10)
        style.map("Primary.TButton",
                 background=[('active', '#006ba3'), ('disabled', '#cccccc')],
                 foreground=[('active', 'white'), ('disabled', '#666666')])
        
        style.configure("Success.TButton",
                       background=self.colors['success'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=10)
        style.map("Success.TButton",
                 background=[('active', '#00a865'), ('disabled', '#cccccc')],
                 foreground=[('active', 'white'), ('disabled', '#666666')])
        
        style.configure("Warning.TButton",
                       background=self.colors['warning'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=10)
        style.map("Warning.TButton",
                 background=[('active', '#f59e0b'), ('disabled', '#cccccc')],
                 foreground=[('active', 'white'), ('disabled', '#666666')])
    
    def create_ui(self):
        # Main container with padding
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header with title and status
        self.create_header(main_container)
        
        # Create tabbed interface
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True, pady=(20, 0))
        
        # Tab 1: Setup & Run
        setup_tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(setup_tab, text='  Setup & Run  ')
        self.create_setup_tab(setup_tab)
        
        # Tab 2: AI Insights
        insights_tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(insights_tab, text='  AI Insights  ')
        self.create_insights_tab(insights_tab)
        
        # Tab 3: Results Log
        log_tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(log_tab, text='  Results Log  ')
        self.create_log_tab(log_tab)
    
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors['bg'])
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Title with ASCII fox
        title_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        title_frame.pack(side='top', pady=10)
        
        # ASCII fox art
        fox_ascii = """    /\\_/\\
   (  o.o)
    > ^ <"""
        
        fox_label = tk.Label(title_frame,
                            text=fox_ascii,
                            font=("Courier", 10),
                            bg=self.colors['bg'],
                            fg=self.colors['primary'],
                            justify='left')
        fox_label.pack(side='left', padx=(0, 15))
        
        title_label = tk.Label(title_frame, 
                               text="fdbckfndr v1.0",
                               font=("Segoe UI", 24, "bold"),
                               bg=self.colors['bg'],
                               fg=self.colors['primary'])
        title_label.pack(side='left')
        
        # Status with loading animation
        status_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        status_frame.pack(fill='x', pady=(5, 0))
        
        self.loading_label = tk.Label(status_frame, 
                                      text="",
                                      font=("Segoe UI", 16),
                                      bg=self.colors['bg'],
                                      fg=self.colors['primary'])
        self.loading_label.pack(side='left', padx=(0, 8))
        
        self.status_label = tk.Label(status_frame, 
                                     text="Ready. Paste your Intercom access token to start.",
                                     font=("Segoe UI", 11, "bold"),
                                     bg=self.colors['bg'],
                                     fg='#574f7d')
        self.status_label.pack(expand=True)
        
        # Loading animation state
        self.loading_active = False
        self.loading_frame = 0
        self.loading_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    def create_setup_tab(self, parent):
        # Credentials Card
        creds_card = tk.Frame(parent, bg=self.colors['card'], bd=1, relief='solid', padx=15, pady=15)
        creds_card.pack(fill='x', pady=(0, 10))
        tk.Label(creds_card, text="Intercom Credentials", font=("Segoe UI", 14, "bold"), 
                 bg=self.colors['card'], fg='#000000').pack(anchor='w')
        tk.Label(creds_card, text="Access Token:", font=("Segoe UI", 10, "bold"), 
                 bg=self.colors['card'], fg='#000000').pack(anchor='w', pady=(5, 0))
        self.token_entry = tk.Entry(creds_card, font=("Segoe UI", 10, "bold"), 
                                    relief='solid', 
                                    borderwidth=1,
                                    bg='white',
                                    fg='#000000',
                                    insertbackground='#000000',
                                    selectbackground='#005482',
                                    selectforeground='white',
                                    show="*")
        self.token_entry.pack(fill='x', pady=(0, 10))
        self.load_teammates_button = tk.Button(creds_card, text="Load Teammates", 
                                               font=("Segoe UI", 11, "bold"), 
                                               bg=self.colors['primary'], 
                                               fg='black', 
                                               activebackground='#006ba3',
                                               activeforeground='white',
                                               disabledforeground='#666666',
                                               relief='flat', 
                                               borderwidth=0,
                                               padx=10,
                                               pady=8,
                                               cursor='hand2',
                                               command=self.start_teammate_thread)
        self.load_teammates_button.pack(fill='x', pady=5)
        
        # Filters Card
        filters_card = tk.Frame(parent, bg=self.colors['card'], bd=1, relief='solid', padx=15, pady=15)
        filters_card.pack(fill='x', pady=(10, 10))
        tk.Label(filters_card, text="Query Filters", font=("Segoe UI", 14, "bold"), 
                 bg=self.colors['card'], fg='#000000').pack(anchor='w')
        tk.Label(filters_card, text="Team (Optional):", font=("Segoe UI", 10, "bold"), 
                 bg=self.colors['card'], fg='#000000').pack(anchor='w', pady=(5, 0))
        self.team_var = tk.StringVar(self.root)
        self.team_var.set("All Teams")
        self.team_var.trace_add('write', self.on_team_selection_change)
        self.team_dropdown = tk.OptionMenu(filters_card, self.team_var, "All Teams")
        self.team_dropdown.config(font=("Segoe UI", 10), 
                                  bg='white', 
                                  fg='#000000',
                                  activebackground='#f0f0f0',
                                  activeforeground='#000000',
                                  relief='solid', 
                                  borderwidth=1,
                                  state='disabled')
        self.team_dropdown.pack(fill='x', pady=(0, 10))
        self.admin_label = tk.Label(filters_card, text="Admin Assignee:", font=("Segoe UI", 10, "bold"), 
                 bg=self.colors['card'], fg='#000000')
        self.admin_label.pack(anchor='w', pady=(5, 0))
        self.admin_var = tk.StringVar(self.root)
        self.admin_var.set("Click 'Load Teammates' first...")
        self.admin_dropdown = ttk.Combobox(filters_card, 
                                           textvariable=self.admin_var,
                                           font=("Segoe UI", 10),
                                           state='disabled')
        self.admin_dropdown.pack(fill='x', pady=(0, 10))
        tk.Label(filters_card, text="Date Range:", font=("Segoe UI", 10, "bold"), 
                 bg=self.colors['card'], fg='#000000').pack(anchor='w')
        date_frame = tk.Frame(filters_card, bg=self.colors['card'])
        date_frame.pack(fill='x', pady=5)
        
        # Start date picker
        start_label = tk.Label(date_frame, text="From:", font=("Segoe UI", 10, "bold"), 
                              bg=self.colors['card'], fg='#000000')
        start_label.pack(side='left', padx=(0, 5))
        
        thirty_days_ago = datetime.now() - timedelta(days=30)
        self.start_date_picker = DatePicker(date_frame, initial_date=thirty_days_ago)
        self.start_date_picker.pack(side='left', padx=(0, 15))
        
        # End date picker
        end_label = tk.Label(date_frame, text="To:", font=("Segoe UI", 10, "bold"), 
                            bg=self.colors['card'], fg='#000000')
        end_label.pack(side='left', padx=(0, 5))
        
        today = datetime.now()
        self.end_date_picker = DatePicker(date_frame, initial_date=today)
        self.end_date_picker.pack(side='left')
        
        # Actions Card
        actions_card = tk.Frame(parent, bg=self.colors['card'], bd=1, relief='solid', padx=15, pady=15)
        actions_card.pack(fill='x', pady=(10, 10))
        tk.Label(actions_card, text="Run Report", font=("Segoe UI", 14, "bold"), 
                 bg=self.colors['card'], fg='#000000').pack(anchor='w')
        self.action_button = tk.Button(actions_card, text="Fetch Report Data", 
                                       font=("Segoe UI", 11, "bold"), 
                                       bg=self.colors['primary'], 
                                       fg='white',
                                       activebackground='#006ba3',
                                       activeforeground='white',
                                       disabledforeground='#666666',
                                       relief='flat',
                                       borderwidth=0,
                                       padx=10,
                                       pady=8,
                                       cursor='hand2',
                                       command=self.start_api_thread)
        self.action_button.pack(fill='x', pady=5)
        self.progressbar = ttk.Progressbar(actions_card, orient='horizontal', 
                                           mode='determinate', length=100, 
                                           style="Modern.Horizontal.TProgressbar")
        self.progressbar.pack(fill='x', pady=5)
        
        # Export buttons in the same card
        tk.Label(actions_card, text="Export Results", font=("Segoe UI", 14, "bold"), 
                 bg=self.colors['card'], fg='#000000').pack(anchor='w', pady=(15, 5))
        btn_frame = tk.Frame(actions_card, bg=self.colors['card'])
        btn_frame.pack(fill='x')
        self.save_csv_button = tk.Button(btn_frame, text="Save as CSV", 
                                         font=("Segoe UI", 11, "bold"), 
                                         bg=self.colors['success'], 
                                         fg='white',
                                         activebackground='#00a865',
                                         activeforeground='white',
                                         disabledforeground='#666666',
                                         relief='flat',
                                         borderwidth=0,
                                         padx=10,
                                         pady=8,
                                         cursor='hand2',
                                         command=self.save_report_to_file, state="disabled")
        self.save_csv_button.pack(side='left', expand=True, fill='x', padx=5, pady=5)
        self.copy_ai_button = tk.Button(btn_frame, text="Copy Remarks for AI", 
                                        font=("Segoe UI", 11, "bold"), 
                                        bg=self.colors['warning'], 
                                        fg='white',
                                        activebackground='#f59e0b',
                                        activeforeground='white',
                                        disabledforeground='#666666',
                                        relief='flat',
                                        borderwidth=0,
                                        padx=10,
                                        pady=8,
                                        cursor='hand2',
                                        command=self.copy_remarks_for_ai, state="disabled")
        self.copy_ai_button.pack(side='left', expand=True, fill='x', padx=5, pady=5)
        
        # Stats Card
        stats_card = tk.Frame(parent, bg=self.colors['card'], bd=1, relief='solid', padx=15, pady=15)
        stats_card.pack(fill='x')
        tk.Label(stats_card, text="Live Stats", font=("Segoe UI", 14, "bold"), 
                 bg=self.colors['card'], fg='#000000').pack(anchor='w')
        
        # Current activity status
        self.current_activity_label = tk.Label(stats_card, text="Status: Ready", 
                                               font=("Segoe UI", 10, "bold"), bg=self.colors['card'], 
                                               fg='#000000', anchor='w', wraplength=800)
        self.current_activity_label.pack(fill='x', pady=2)
        
        # Page and progress info
        self.page_label = tk.Label(stats_card, text="Page: 0 / 0", 
                                   font=("Segoe UI", 11, "bold"), bg=self.colors['card'], 
                                   fg='#000000', anchor='w')
        self.page_label.pack(fill='x', pady=2)
        
        self.scanned_label = tk.Label(stats_card, text="Scanned: 0 / 0 conversations", 
                                      font=("Segoe UI", 11, "bold"), bg=self.colors['card'], 
                                      fg='#000000', anchor='w')
        self.scanned_label.pack(fill='x', pady=2)
        
        # Current page details
        self.current_page_info_label = tk.Label(stats_card, text="Current page: Not started", 
                                                font=("Segoe UI", 10), bg=self.colors['card'], 
                                                fg='#666666', anchor='w', wraplength=800)
        self.current_page_info_label.pack(fill='x', pady=2)
        
        self.found_label = tk.Label(stats_card, text="Remarks found: 0", 
                                    font=("Segoe UI", 11, "bold"), bg=self.colors['card'], 
                                    fg='#000000', anchor='w')
        self.found_label.pack(fill='x', pady=2)
        
        self.etr_label = tk.Label(stats_card, text="ETR: N/A", 
                                  font=("Segoe UI", 11, "bold"), bg=self.colors['card'], 
                                  fg='#000000', anchor='w')
        self.etr_label.pack(fill='x', pady=2)
    
    def create_insights_tab(self, parent):
        # AI Insights Card
        ai_card = tk.Frame(parent, bg=self.colors['card'], bd=1, relief='solid', padx=15, pady=15)
        ai_card.pack(fill='both', expand=True, pady=(0, 10))
        tk.Label(ai_card, text="AI-Powered Feedback Analysis", font=("Segoe UI", 14, "bold"), 
                 bg=self.colors['card'], fg='#000000').pack(anchor='w')
        tk.Label(ai_card, text="Analyze customer feedback for actionable insights.", 
                 font=("Segoe UI", 10, "bold"), bg=self.colors['card'], 
                 fg='#000000').pack(anchor='w', pady=(0, 10))
        self.analyze_button = tk.Button(ai_card, text="Analyze Feedback with AI", 
                                        font=("Segoe UI", 11, "bold"), 
                                        bg=self.colors['primary'], 
                                        fg='white',
                                        activebackground='#006ba3',
                                        activeforeground='white',
                                        disabledforeground='#666666',
                                        relief='flat',
                                        borderwidth=0,
                                        padx=10,
                                        pady=8,
                                        cursor='hand2',
                                        command=self.start_ai_analysis, state="disabled")
        self.analyze_button.pack(fill='x', pady=5)
        self.ai_result_text = scrolledtext.ScrolledText(ai_card, font=("Segoe UI", 11, "bold"), 
                                                        relief='solid', 
                                                        borderwidth=1,
                                                        bg='white',
                                                        fg='#000000',
                                                        insertbackground='#000000',
                                                        selectbackground='#005482',
                                                        selectforeground='white',
                                                        height=15, 
                                                        wrap=tk.WORD)
        self.ai_result_text.pack(fill='both', expand=True, pady=10)
        self.ai_result_text.configure(state='disabled')
        
        # Sentiment Summary Card
        sentiment_card = tk.Frame(parent, bg=self.colors['card'], bd=1, relief='solid', padx=15, pady=15)
        sentiment_card.pack(fill='x', pady=(10, 0))
        tk.Label(sentiment_card, text="Sentiment Summary", font=("Segoe UI", 14, "bold"), 
                 bg=self.colors['card'], fg='#000000').pack(anchor='w')
        self.sentiment_label = tk.Label(sentiment_card, text="No analysis yet. Run AI analysis after fetching data.", 
                                        font=("Segoe UI", 11, "bold"), bg=self.colors['card'], 
                                        fg='#000000', anchor='w')
        self.sentiment_label.pack(fill='x', pady=5)
    
    def create_log_tab(self, parent):
        log_card = tk.Frame(parent, bg=self.colors['card'], bd=1, relief='solid', padx=15, pady=15)
        log_card.pack(fill='both', expand=True)
        tk.Label(log_card, text="Results Log", font=("Segoe UI", 14, "bold"), 
                 bg=self.colors['card'], fg='#000000').pack(anchor='w')
        self.log_widget = scrolledtext.ScrolledText(log_card, font=("Courier New", 11, "bold"), 
                                                    relief='solid', 
                                                    borderwidth=1,
                                                    bg='white',
                                                    fg='#000000',
                                                    insertbackground='#000000',
                                                    selectbackground='#005482',
                                                    selectforeground='white',
                                                    height=25, 
                                                    wrap=tk.WORD)
        self.log_widget.pack(fill='both', expand=True, pady=5)
        self.log_widget.configure(state='disabled')
    
    def log_message(self, message):
        self.log_widget.configure(state='normal')
        self.log_widget.insert('end', message + '\n')
        self.log_widget.see('end')
        self.log_widget.configure(state='disabled')
    
    def start_teammate_thread(self):
        token = self.token_entry.get()
        if not token:
            messagebox.showerror("Error", "Please paste your Access Token first.")
            return
        self.log_message("Fetching teammate list...")
        self.status_label.config(text="Fetching teammate list...")
        self.load_teammates_button.config(text="Loading...", state="disabled")
        self.start_loading()
        threading.Thread(target=self.run_teammate_fetch, args=(token,), daemon=True).start()
    
    def run_teammate_fetch(self, token):
        admin_map = {}
        team_map = {}
        team_admins_map = {}  # Map team_id to list of admin_ids
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        
        # Fetch teams
        try:
            teams_url = "https://api.intercom.io/teams"
            teams_response = requests.get(teams_url, headers=headers)
            teams_response.raise_for_status()
            teams_data = teams_response.json()
            for team in teams_data.get('teams', []):
                name = team.get('name', 'Unknown')
                team_id = team.get('id')
                if name and team_id:
                    team_map[name] = str(team_id)
                    # Initialize empty list for team admins
                    team_admins_map[str(team_id)] = []
        except requests.exceptions.RequestException as e:
            self.log_queue.put(f"Note: Could not fetch teams: {e}")
        
        # Fetch admins and map them to teams
        url = "https://api.intercom.io/admins"
        params = {"page": 1}
        try:
            while True:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                for admin in data.get('admins', []):
                    name = admin.get('name', 'Unknown')
                    email = admin.get('email', '')
                    admin_id = admin.get('id')
                    admin_teams = admin.get('team_ids', [])
                    admin_map[f"{name} ({email})"] = str(admin_id)
                    
                    # Map admin to teams
                    for team_id in admin_teams:
                        team_id_str = str(team_id)
                        if team_id_str in team_admins_map:
                            team_admins_map[team_id_str].append(str(admin_id))
                if data.get('pages') and data['pages'].get('next'):
                    params['page'] += 1
                else:
                    break
            self.log_queue.put(("ADMIN_LIST_DONE", admin_map, team_map, team_admins_map))
        except requests.exceptions.RequestException as e:
            self.log_queue.put(f"!!! FAILED to fetch teammates: {e}")
            self.log_queue.put("(Check your token - might need more permissions)")
            self.log_queue.put(("ADMIN_LOAD_FAILED",))
    
    def populate_admin_dropdown(self):
        sorted_admin_names = sorted(self.admin_map.keys())
        
        # Build values list with optional placeholder
        admin_values = ["(Optional - not needed if team selected)"] + sorted_admin_names
        self.admin_dropdown['values'] = admin_values
        
        # Set default based on current team selection
        team_name = self.team_var.get()
        if team_name and team_name != "All Teams":
            self.admin_var.set("(Optional - not needed if team selected)")
        else:
            self.admin_var.set("Select an admin...")
        
        self.admin_dropdown.config(state="normal")
        
        # Populate team dropdown
        team_menu = self.team_dropdown["menu"]
        team_menu.delete(0, "end")
        team_menu.add_command(label="All Teams", command=lambda: self.team_var.set("All Teams"))
        if self.team_map:
            sorted_team_names = sorted(self.team_map.keys())
            for name in sorted_team_names:
                team_menu.add_command(label=name, command=lambda value=name: self.team_var.set(value))
        self.team_dropdown.config(state="normal")
        
        # Update admin field state based on team selection
        self.on_team_selection_change()
        
        self.log_message(f"✅ Successfully loaded {len(self.admin_map)} active teammates.")
        if self.team_map:
            self.log_message(f"✅ Successfully loaded {len(self.team_map)} teams.")
        self.status_label.config(text="Teammates loaded. Ready to fetch report.")
        if len(self.admin_map) > 0:
            self.log_message("(Teammates Loaded)")
        self.load_teammates_button.config(text="Load Teammates", state="normal")
        self.stop_loading()
    
    def on_team_selection_change(self, *args):
        """Update admin field state and label based on team selection"""
        team_name = self.team_var.get()
        if team_name and team_name != "All Teams":
            # Team selected - admin is optional
            self.admin_label.config(text="Admin Assignee (Optional):")
            # Auto-set to optional if currently set to "Select an admin..."
            if self.admin_var.get() == "Select an admin...":
                self.admin_var.set("(Optional - not needed if team selected)")
            self.admin_dropdown.config(state="normal")
        else:
            # No team selected - admin is required
            self.admin_label.config(text="Admin Assignee:")
            # Auto-set to "Select an admin..." if currently set to optional
            if self.admin_var.get() == "(Optional - not needed if team selected)":
                self.admin_var.set("Select an admin...")
            self.admin_dropdown.config(state="normal")
    
    def start_api_thread(self):
        token = self.token_entry.get()
        start_date_str = self.start_date_picker.get_date()
        end_date_str = self.end_date_picker.get_date()
        admin_name = self.admin_var.get()
        team_name = self.team_var.get()
        
        # Determine team_id
        team_id = None
        if team_name and team_name != "All Teams" and team_name in self.team_map:
            team_id = self.team_map[team_name]
        
        # Validate: either team or admin must be selected
        admin_id = None
        if admin_name and admin_name != "Select an admin..." and admin_name != "(Optional - not needed if team selected)":
            if admin_name in self.admin_map:
                admin_id = self.admin_map[admin_name]
        
        if not team_id and not admin_id:
            messagebox.showerror("Error", "Please select either a team or an admin (or both) from the dropdowns.")
            return
        
        if not token:
            messagebox.showerror("Error", "Please enter an Intercom Token.")
            return
        try:
            datetime.strptime(start_date_str, "%Y-%m-%d")
            datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter dates in YYYY-MM-DD format.")
            return
        self.log_widget.configure(state='normal')
        self.log_widget.delete('1.0', 'end')
        self.log_widget.configure(state='disabled')
        self.status_label.config(text="Starting... Fetching first page...")
        self.action_button.config(text="Running...", state='disabled')
        self.save_csv_button.config(state='disabled')
        self.copy_ai_button.config(state='disabled')
        self.analyze_button.config(state='disabled')
        self.progressbar['value'] = 0
        self.scanned_label.config(text="Scanned: 0 / 0 conversations")
        self.page_label.config(text="Page: 0 / 0")
        self.found_label.config(text="Remarks found: 0")
        self.etr_label.config(text="ETR: Calculating...")
        self.current_activity_label.config(text="Status: Starting... Fetching first page...")
        self.current_page_info_label.config(text="Current page: Not started")
        self.final_report_data.clear()
        self.total_found = 0
        self.start_time = time.monotonic()
        self.start_loading()
        threading.Thread(target=self.run_api_script, args=(token, admin_id, start_date_str, end_date_str, team_id), daemon=True).start()
    
    def run_api_script(self, intercom_token, admin_id, start_date_str, end_date_str, team_id=None):
        try:
            start_ts = str(int(datetime.strptime(start_date_str, "%Y-%m-%d").timestamp()))
            end_date_dt = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1)
            end_ts = str(int(end_date_dt.timestamp()))
        except Exception as e:
            self.log_queue.put(f"!!! Date conversion error: {e}")
            self.log_queue.put(("DONE", 0))
            return
        intercom_url = "https://api.intercom.io/conversations/search"
        intercom_headers = {"Authorization": f"Bearer {intercom_token}", "Accept": "application/json", "Content-Type": "application/json"}
        
        # Build base filters (date and rating)
        base_filters = [
            {"field": "created_at", "operator": ">", "value": start_ts},
            {"field": "created_at", "operator": "<", "value": end_ts},
            {"field": "conversation_rating.score", "operator": "IN", "value": [1, 2, 3, 4, 5]}
        ]
        
        # Handle team selection: get all admins in the team
        if team_id:
            team_admin_ids = self.team_admins_map.get(team_id, [])
            if not team_admin_ids:
                self.log_queue.put(f"!!! WARNING: No admins found for team {team_id}. Cannot search.")
                self.log_queue.put(("DONE", 0))
                return
            
            # If specific admin is also selected, filter to that admin (must be in team)
            if admin_id and admin_id in team_admin_ids:
                # Single admin selected within team
                admin_filter = {"field": "admin_assignee_id", "operator": "=", "value": admin_id}
                query_filters = base_filters + [admin_filter]
                query_operator = "AND"
            else:
                if admin_id:
                    self.log_queue.put(f"!!! WARNING: Selected admin is not in the selected team. Searching all team admins instead.")
                
                # Multiple admins - Intercom API has limits on OR query size
                # If too many admins, we'll need to make multiple queries
                num_admins = len(team_admin_ids)
                self.log_queue.put(f"Team has {num_admins} admins. Building query...")
                
                # Intercom API typically supports up to ~20 OR conditions
                # If more than that, we'll split into multiple queries
                MAX_OR_CONDITIONS = 15
                
                if num_admins <= MAX_OR_CONDITIONS:
                    # Small enough for single query
                    admin_or_conditions = []
                    for aid in team_admin_ids:
                        admin_or_conditions.append({"field": "admin_assignee_id", "operator": "=", "value": aid})
                    
                    # Combine: (base_filters AND) AND (admin1 OR admin2 OR ...)
                    query_filters = [
                        {"operator": "AND", "value": base_filters},
                        {"operator": "OR", "value": admin_or_conditions}
                    ]
                    query_operator = "AND"
                else:
                    # Too many admins - split into multiple queries
                    self.log_queue.put(f"Splitting {num_admins} admins into batches of {MAX_OR_CONDITIONS}...")
                    all_results = []
                    for i in range(0, num_admins, MAX_OR_CONDITIONS):
                        batch = team_admin_ids[i:i + MAX_OR_CONDITIONS]
                        self.log_queue.put(f"Processing batch {i//MAX_OR_CONDITIONS + 1} with {len(batch)} admins...")
                        
                        admin_or_conditions = []
                        for aid in batch:
                            admin_or_conditions.append({"field": "admin_assignee_id", "operator": "=", "value": aid})
                        
                        query_filters = [
                            {"operator": "AND", "value": base_filters},
                            {"operator": "OR", "value": admin_or_conditions}
                        ]
                        query_operator = "AND"
                        batch_payload = {
                            "query": {"operator": query_operator, "value": query_filters},
                            "pagination": {"per_page": 42}
                        }
                        
                        # Process this batch
                        batch_results = self._process_query_batch(intercom_url, intercom_headers, batch_payload, i//MAX_OR_CONDITIONS + 1)
                        all_results.extend(batch_results)
                    
                    # Combine all results
                    self.final_report_data.extend(all_results)
                    self.total_found = len(all_results)
                    self.log_queue.put(f"\n✅ Fetch complete. Found {len(all_results)} total remarks across all batches.")
                    if len(all_results) > 50:
                        self.log_queue.put("(That's a lot of feedback to hunt through!)")
                    self.log_queue.put(("TRIGGER_ENABLE_EXPORT", len(all_results)))
                    self.log_queue.put(("DONE", len(all_results)))
                    return
        elif admin_id:
            # No team selected, just filter by admin
            admin_filter = {"field": "admin_assignee_id", "operator": "=", "value": admin_id}
            query_filters = base_filters + [admin_filter]
            query_operator = "AND"
        else:
            # No filters (shouldn't happen due to validation, but handle it)
            query_filters = base_filters
            query_operator = "AND"
        
        # Only build payload if we haven't already handled team splitting
        if team_id and len(self.team_admins_map.get(team_id, [])) > 15:
            # Already handled in the team splitting logic above
            return
        
        payload = {
            "query": { "operator": query_operator, "value": query_filters},
            "pagination": {"per_page": 42}
        }
        
        # Build log message
        search_info = []
        if team_id:
            team_name = [name for name, tid in self.team_map.items() if tid == team_id]
            search_info.append(f"team: {team_name[0] if team_name else team_id}")
        if admin_id:
            admin_name = [name for name, aid in self.admin_map.items() if aid == admin_id]
            search_info.append(f"admin: {admin_name[0] if admin_name else admin_id}")
        search_str = ", ".join(search_info) if search_info else "all conversations"
        self.log_queue.put(f"Fetching remarks for {search_str} from {start_date_str} to {end_date_str}...")
        
        # Process the query
        self._run_single_query(intercom_url, intercom_headers, payload, start_date_str, end_date_str)
    
    def _run_single_query(self, intercom_url, intercom_headers, payload, start_date_str, end_date_str):
        """Process a single query with pagination"""
        page = 1
        is_first_page = True
        while True:
            try:
                self.log_queue.put(f"📄 Fetching page {page}...")
                self.log_queue.put(("CURRENT_ACTIVITY", f"📄 Fetching page {page}..."))
                response = requests.post(intercom_url, headers=intercom_headers, data=json.dumps(payload))
                response.raise_for_status()
                data = response.json()
                
                if is_first_page:
                    page_1_end_time = time.monotonic()
                    self.time_per_page = page_1_end_time - self.start_time
                    total_convos = data.get('total_count', 0)
                    total_pages = data.get('pages', {}).get('total_pages', 1)
                    initial_etr = self.time_per_page * (total_pages - 1)
                    self.log_queue.put(f"📊 Found {total_convos} total conversations across {total_pages} pages")
                    self.log_queue.put(("STATS_INIT", total_convos, total_pages, initial_etr))
                    self.log_queue.put(("CURRENT_ACTIVITY", f"📊 Found {total_convos} total conversations across {total_pages} pages"))
                    is_first_page = False
                
                conversations = data.get("conversations", [])
                if not conversations:
                    self.log_queue.put("No more conversations found.")
                    break
                
                self.log_queue.put(f"📦 Processing {len(conversations)} conversations from page {page}...")
                self.log_queue.put(("CURRENT_ACTIVITY", f"📦 Processing {len(conversations)} conversations from page {page}..."))
                self.log_queue.put(("CURRENT_PAGE_INFO", f"Processing {len(conversations)} conversations..."))
                found_on_page = 0
                processed_count = 0
                
                for idx, convo in enumerate(conversations, 1):
                    processed_count += 1
                    convo_id = convo.get('id', 'Unknown')
                    convo_date = convo.get('created_at', 0)
                    readable_date = datetime.fromtimestamp(convo_date).strftime('%Y-%m-%d %H:%M') if convo_date else 'N/A'
                    
                    # Check if conversation has a rating with remark
                    if (convo.get("conversation_rating") and convo["conversation_rating"].get("remark") is not None):
                        remark = convo['conversation_rating'].get('remark')
                        rating = convo['conversation_rating'].get('rating', 'N/A')
                        
                        self.log_queue.put(f"  ✓ Conversation {idx}/{len(conversations)} (ID: {convo_id[:8]}...): Rating {rating}, Date: {readable_date}")
                        self.log_queue.put(f"    Processing remark: {remark[:80]}{'...' if len(remark) > 80 else ''}")
                        
                        # Translate if needed
                        translated_remark = self.translate_if_non_english(remark)
                        if translated_remark != remark:
                            self.log_queue.put(f"    ✓ Translated to English")
                        
                        report_item = {
                            "id": convo_id,
                            "rating": rating,
                            "date": convo_date,
                            "remark": remark
                        }
                        # Only store translated_remark if it's actually different
                        if translated_remark != remark:
                            report_item["translated_remark"] = translated_remark
                        self.final_report_data.append(report_item)
                        found_on_page += 1
                    else:
                        self.log_queue.put(f"  ○ Conversation {idx}/{len(conversations)} (ID: {convo_id[:8]}...): No remark found")
                
                self.log_queue.put(f"✅ Page {page} complete: Found {found_on_page} remarks out of {len(conversations)} conversations")
                self.log_queue.put(("CURRENT_ACTIVITY", f"✅ Page {page} complete: {found_on_page} remarks found"))
                self.log_queue.put(("CURRENT_PAGE_INFO", f"Page {page}: {found_on_page} remarks found out of {len(conversations)} conversations"))
                self.log_queue.put(("PAGE_UPDATE", page, found_on_page))
                
                # Check for next page
                pages_data = data.get("pages", {})
                if pages_data.get("next"):
                    next_cursor = pages_data["next"].get("starting_after")
                    if next_cursor:
                        payload["pagination"] = {"per_page": 42, "starting_after": next_cursor}
                        page += 1
                    else:
                        break
                else:
                    break
            except requests.exceptions.RequestException as e:
                error_msg = f"!!! INTERCOM API ERROR: {e}"
                self.log_queue.put(error_msg)
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_details = e.response.json()
                        self.log_queue.put(f"Error response: {json.dumps(error_details, indent=2)}")
                    except:
                        self.log_queue.put(f"Error details: {e.response.text}")
                    self.log_queue.put(f"Request payload was: {json.dumps(payload, indent=2)}")
                self.log_queue.put(("DONE", 0))
                return
        if not self.final_report_data:
            self.log_queue.put("No remarks found for this query.")
            self.log_queue.put("(Maybe try a different date range?)")
        else:
            self.log_queue.put(f"\n✅ Fetch complete. Found {self.total_found} total remarks.")
            if self.total_found > 100:
                self.log_queue.put("(Solid catch!)")
            self.log_queue.put(("TRIGGER_ENABLE_EXPORT", self.total_found))
        self.log_queue.put(("DONE", self.total_found))
    
    def _process_query_batch(self, intercom_url, intercom_headers, payload, batch_num):
        """Process a single batch query and return results"""
        batch_results = []
        page = 1
        
        while True:
            try:
                self.log_queue.put(f"📄 Batch {batch_num} - Fetching page {page}...")
                response = requests.post(intercom_url, headers=intercom_headers, data=json.dumps(payload))
                response.raise_for_status()
                data = response.json()
                
                conversations = data.get("conversations", [])
                if not conversations:
                    break
                
                self.log_queue.put(f"📦 Batch {batch_num} - Processing {len(conversations)} conversations from page {page}...")
                
                for idx, convo in enumerate(conversations, 1):
                    convo_id = convo.get('id', 'Unknown')
                    convo_date = convo.get('created_at', 0)
                    readable_date = datetime.fromtimestamp(convo_date).strftime('%Y-%m-%d %H:%M') if convo_date else 'N/A'
                    
                    if (convo.get("conversation_rating") and convo["conversation_rating"].get("remark") is not None):
                        remark = convo['conversation_rating'].get('remark')
                        rating = convo['conversation_rating'].get('rating', 'N/A')
                        
                        self.log_queue.put(f"  ✓ Batch {batch_num} - Conversation {idx}/{len(conversations)} (ID: {convo_id[:8]}...): Rating {rating}")
                        
                        translated_remark = self.translate_if_non_english(remark)
                        
                        report_item = {
                            "id": convo_id,
                            "rating": rating,
                            "date": convo_date,
                            "remark": remark
                        }
                        # Only store translated_remark if it's actually different
                        if translated_remark != remark:
                            report_item["translated_remark"] = translated_remark
                        batch_results.append(report_item)
                
                pages_data = data.get("pages", {})
                if pages_data.get("next"):
                    next_cursor = pages_data["next"].get("starting_after")
                    if next_cursor:
                        payload["pagination"] = {"per_page": 42, "starting_after": next_cursor}
                        page += 1
                    else:
                        break
                else:
                    break
            except requests.exceptions.RequestException as e:
                error_msg = f"!!! INTERCOM API ERROR in batch {batch_num}: {e}"
                self.log_queue.put(error_msg)
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_details = e.response.json()
                        self.log_queue.put(f"Error response: {json.dumps(error_details, indent=2)}")
                    except:
                        self.log_queue.put(f"Error details: {e.response.text}")
                break
        
        self.log_queue.put(f"✅ Batch {batch_num} complete: Found {len(batch_results)} remarks")
        return batch_results
    
    def translate_if_non_english(self, text):
        if not text:
            return text
        try:
            # Check if already translated
            if text in self.translations_cache:
                return self.translations_cache[text]
            # Translate (deep-translator auto-detects language and only translates if needed)
            translated = self.translator.translate(text)
            # If translation is the same as original, it's likely already English
            if translated.lower() == text.lower():
                self.translations_cache[text] = text
                return text
            self.translations_cache[text] = translated
            # Log translation (this will be queued and processed by the main thread)
            self.log_queue.put(f"    🌐 Translation: {translated[:60]}{'...' if len(translated) > 60 else ''}")
            return translated
        except Exception as e:
            self.log_queue.put(f"    ⚠️ Translation error: {e}")
            return text
    
    def save_report_to_file(self):
        if not self.final_report_data:
            messagebox.showinfo("No Data", "There are no remarks to save.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV (Comma-separated values)", "*.csv"), ("All Files", "*.*")],
            title="Save Remarks Report",
            initialfile="remarks-report.csv"
        )
        if not file_path:
            self.log_message("Save operation cancelled.")
            return
        try:
            with open(file_path, "w", encoding="utf-8", newline='') as f:
                headers = ["ID", "Rating", "Date", "Remark", "Translated Remark"]
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for item in self.final_report_data:
                    readable_date = datetime.fromtimestamp(item['date']).strftime('%Y-%m-%d %H:%M:%S')
                    row = {
                        "ID": item['id'],
                        "Rating": item['rating'],
                        "Date": readable_date,
                        "Remark": item['remark'],
                        "Translated Remark": item.get('translated_remark', '')
                    }
                    writer.writerow(row)
            self.log_message(f"\n✅ Report successfully saved to:\n{file_path}")
            self.log_message("\nYou can now open this file in Excel or Google Sheets.")
            self.status_label.config(text=f"Report saved to {file_path}")
            if len(self.final_report_data) > 0:
                self.log_message("(Ready to analyze!)")
        except Exception as e:
            self.log_message(f"\n!!! FAILED TO SAVE FILE: {e}")
            messagebox.showerror("Save Error", f"Could not save the file: {e}")
    
    def copy_remarks_for_ai(self):
        if not self.final_report_data:
            messagebox.showinfo("No Data", "There are no remarks to copy.")
            return
        try:
            remarks_list = [item.get('translated_remark', item['remark']) for item in self.final_report_data]
            all_remarks_text = "\n".join(remarks_list)
            self.root.clipboard_clear()
            self.root.clipboard_append(all_remarks_text)
            self.log_message(f"\n✅ Copied {len(remarks_list)} remarks to the clipboard.")
            self.log_message("You can now paste this into chat.consensys.net.")
            self.status_label.config(text=f"Copied {len(remarks_list)} remarks to clipboard.")
            if len(remarks_list) > 20:
                self.log_message("(That's a lot of data - hope your clipboard can handle it!)")
        except Exception as e:
            self.log_message(f"\n!!! FAILED TO COPY: {e}")
            messagebox.showerror("Copy Error", f"Could not copy to clipboard: {e}")
    
    def start_ai_analysis(self):
        if not self.final_report_data:
            messagebox.showinfo("No Data", "There are no remarks to analyze.")
            return
        self.analyze_button.config(text="Analyzing...", state='disabled')
        self.status_label.config(text="Running AI analysis...")
        threading.Thread(target=self.run_ai_analysis, daemon=True).start()
    
    def run_ai_analysis(self):
        try:
            remarks = [item.get('translated_remark', item['remark']) for item in self.final_report_data]
            prompt = f"Analyze the following customer feedback remarks from Intercom for sentiment, common themes, and actionable insights. Provide a summary with bullet points.\n\nFeedback:\n" + "\n".join(remarks)
            openai.api_key = self.openai_api_key
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )
            analysis_text = response.choices[0].text.strip()
            self.ai_insights = {"summary": analysis_text}
            self.log_queue.put(("AI_ANALYSIS_DONE", analysis_text))
            
            # Simple sentiment calculation (placeholder for more advanced analysis)
            positive_count = sum(1 for item in self.final_report_data if item['rating'] >= 4)
            negative_count = sum(1 for item in self.final_report_data if item['rating'] <= 2)
            neutral_count = sum(1 for item in self.final_report_data if item['rating'] == 3)
            total = len(self.final_report_data)
            sentiment_summary = f"Positive: {positive_count} ({positive_count/total*100:.1f}%) | Neutral: {neutral_count} ({neutral_count/total*100:.1f}%) | Negative: {negative_count} ({negative_count/total*100:.1f}%)"
            self.log_queue.put(("SENTIMENT_SUMMARY", sentiment_summary))
        except Exception as e:
            self.log_queue.put(f"!!! AI ANALYSIS ERROR: {e}")
            self.log_queue.put(("AI_ANALYSIS_FAILED",))
    
    def process_queue(self):
        try:
            message = self.log_queue.get_nowait()
            if isinstance(message, tuple):
                msg_type = message[0]
                if msg_type == "ADMIN_LIST_DONE":
                    self.admin_map = message[1]
                    if len(message) > 2:
                        self.team_map = message[2]
                    if len(message) > 3:
                        self.team_admins_map = message[3]
                    self.populate_admin_dropdown()
                elif msg_type == "ADMIN_LOAD_FAILED":
                    self.log_message("Failed to load teammates. Check token and permissions.")
                    self.status_label.config(text="Failed to load teammates.")
                    self.load_teammates_button.config(text="Load Teammates", state="normal")
                    self.stop_loading()
                elif msg_type == "STATS_INIT":
                    self.total_conversations, self.total_pages, etr = message[1], message[2], message[3]
                    self.progressbar['maximum'] = self.total_conversations
                    self.scanned_label.config(text=f"Scanned: 0 / {self.total_conversations} conversations")
                    self.page_label.config(text=f"Page: 0 / {self.total_pages}")
                    self.etr_label.config(text=f"ETR: {etr:.0f} seconds")
                elif msg_type == "CURRENT_ACTIVITY":
                    activity_text = message[1]
                    self.current_activity_label.config(text=f"Status: {activity_text}")
                elif msg_type == "CURRENT_PAGE_INFO":
                    page_info = message[1]
                    self.current_page_info_label.config(text=f"Current page: {page_info}")
                elif msg_type == "PAGE_UPDATE":
                    page_num, found_on_page = message[1], message[2]
                    self.total_found += found_on_page
                    scanned_so_far = min(page_num * 42, self.total_conversations)
                    remaining_pages = self.total_pages - page_num
                    new_etr = self.time_per_page * remaining_pages
                    self.progressbar['value'] = scanned_so_far
                    self.scanned_label.config(text=f"Scanned: {scanned_so_far} / {self.total_conversations} conversations")
                    self.page_label.config(text=f"Page: {page_num} / {self.total_pages}")
                    self.found_label.config(text=f"Remarks found: {self.total_found}")
                    self.etr_label.config(text=f"ETR: {new_etr:.0f} seconds")
                    # Don't duplicate log message here as it's already logged in the thread
                elif msg_type == "TRIGGER_ENABLE_EXPORT":
                    self.status_label.config(text="Fetch complete. Ready to export.")
                    self.action_button.config(text="Fetch Report Data", state='normal')
                    self.progressbar['value'] = self.total_conversations
                    self.etr_label.config(text="ETR: 0 seconds")
                    self.save_csv_button.config(state='normal')
                    self.copy_ai_button.config(state='normal')
                    self.analyze_button.config(state='normal')
                    self.stop_loading()
                elif msg_type == "DONE":
                    total_count = message[1]
                    self.status_label.config(text=f"Process Complete. Found {total_count} remarks.")
                    self.action_button.config(text="Fetch Report Data", state='normal')
                    self.etr_label.config(text="ETR: 0 seconds")
                    if self.total_conversations > 0:
                        self.progressbar['value'] = self.total_conversations
                    self.stop_loading()
                elif msg_type == "AI_ANALYSIS_DONE":
                    analysis_text = message[1]
                    self.ai_result_text.configure(state='normal')
                    self.ai_result_text.delete('1.0', 'end')
                    self.ai_result_text.insert('end', analysis_text)
                    self.ai_result_text.configure(state='disabled')
                    self.log_message("✅ AI analysis complete.")
                    self.analyze_button.config(text="Analyze Feedback with AI", state='normal')
                    self.status_label.config(text="AI analysis complete.")
                elif msg_type == "SENTIMENT_SUMMARY":
                    summary = message[1]
                    self.sentiment_label.config(text=summary)
                elif msg_type == "AI_ANALYSIS_FAILED":
                    self.log_message("Failed to run AI analysis. Check API key or connectivity.")
                    self.analyze_button.config(text="Analyze Feedback with AI", state='normal')
                    self.status_label.config(text="AI analysis failed.")
            else:
                self.log_message(str(message))
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)
    
    def start_loading(self):
        """Start the loading animation"""
        self.loading_active = True
        self.loading_frame = 0
        self.loading_label.config(text=self.loading_frames[0], fg=self.colors['primary'])
    
    def stop_loading(self):
        """Stop the loading animation"""
        self.loading_active = False
        self.loading_label.config(text="")
    
    def animate_loading(self):
        """Animate the loading spinner"""
        if self.loading_active:
            self.loading_label.config(text=self.loading_frames[self.loading_frame])
            self.loading_frame = (self.loading_frame + 1) % len(self.loading_frames)
        self.root.after(100, self.animate_loading)
    
    def show_about(self):
        messagebox.showinfo("About Intercom Insights", "Intercom Insights Pro v2.0\nFetches remarks, translates non-English feedback, and provides AI-powered insights.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernIntercomApp(root)
    root.mainloop()