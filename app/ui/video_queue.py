import tkinter as tk
from tkinter import ttk, messagebox
from app.core.app import YTManagerApp
from app.utils.logger import setup_logging
from PIL import Image, ImageTk, ImageDraw

logger = setup_logging()

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Ensure frame width matches canvas
        def configure_frame_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", configure_frame_width)

        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mouse wheel events for scrolling
        def _on_mousewheel(event):
            # Windows and Linux
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def _on_mousewheel_linux(event):
            # Linux alternative
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
        
        # Bind mouse wheel to canvas and scrollable frame
        canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
        canvas.bind("<Button-4>", _on_mousewheel_linux)  # Linux scroll up
        canvas.bind("<Button-5>", _on_mousewheel_linux)  # Linux scroll down
        
        # Also bind to the scrollable frame so scrolling works when hovering over it
        self.scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        self.scrollable_frame.bind("<Button-4>", _on_mousewheel_linux)
        self.scrollable_frame.bind("<Button-5>", _on_mousewheel_linux)
        
        # Bind to parent window when mouse enters canvas area (for better Windows support)
        # This ensures mouse wheel works even when canvas doesn't have focus
        def _on_enter(event):
            container.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _on_leave(event):
            container.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", _on_enter)
        canvas.bind("<Leave>", _on_leave)
        self.scrollable_frame.bind("<Enter>", _on_enter)
        self.scrollable_frame.bind("<Leave>", _on_leave)
        
        # Store canvas reference for potential future use
        self.canvas = canvas

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class MainWindow(tk.Tk):
    def __init__(self, app_logic: YTManagerApp):
        super().__init__()
        self.app_logic = app_logic
        self.title("YT Manager v1")
        self.geometry("1100x600")

        self._set_icon()
        self._create_widgets()
        self._bind_shortcuts()
        self.refresh_table()

    def _set_icon(self):
        """Sets the window icon by generating a PNG using Pillow."""
        try:
            # Generate a 64x64 icon in memory
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Red Rectangle with rounded corners (approximated)
            # Pillow's rounded_rectangle requires newer version, or we just draw rect
            rect_color = "#FF0000"
            draw.rounded_rectangle((4, 12, 60, 52), radius=10, fill=rect_color)
            
            # White 'Y' - simple text drawing
            # We try to load a default font, or fallback
            # If we can't load a font easily, we can draw lines for 'Y'
            
            # Drawing 'Y' manually with lines for reliability without font files
            # Center is roughly 32, 32
            # Top-left of Y: 22, 25
            # Top-right of Y: 42, 25
            # Middle join: 32, 38
            # Bottom: 32, 48
            
            line_color = "white"
            line_width = 4
            draw.line((24, 22, 32, 34), fill=line_color, width=line_width) # Left arm
            draw.line((40, 22, 32, 34), fill=line_color, width=line_width) # Right arm
            draw.line((32, 34, 32, 46), fill=line_color, width=line_width) # Stem

            self.icon_photo = ImageTk.PhotoImage(img)
            self.iconphoto(True, self.icon_photo)
            
        except Exception as e:
            logger.error(f"Failed to set window icon: {e}")

    def _bind_shortcuts(self):
        """Bind global keyboard shortcuts."""
        self.bind("<F5>", lambda event: self.refresh_table())
        # When the main window gains focus, set focus to the URL entry
        self.bind("<FocusIn>", lambda event: self._on_focus_in(event))

    def _on_focus_in(self, event):
        # Only focus if the event widget is the root window (to avoid stealing focus from other widgets)
        if event.widget == self:
            self.url_entry.focus_set()
            self.url_entry.select_range(0, tk.END)

    def _create_widgets(self):
        # Top Frame: Add Video
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill="x")

        ttk.Label(top_frame, text="Video URL:").pack(side="left", padx=5)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(top_frame, textvariable=self.url_var, width=60)
        self.url_entry.pack(side="left", padx=5)
        self.url_entry.bind("<Return>", lambda event: self.add_video()) # Bind Enter key
        
        add_btn = ttk.Button(top_frame, text="Add Video", command=self.add_video)
        add_btn.pack(side="left", padx=5)

        # Middle Frame: Video List
        mid_frame = ttk.Frame(self, padding=10)
        mid_frame.pack(fill="both", expand=True)

        # Headers
        headers_frame = ttk.Frame(mid_frame)
        headers_frame.pack(fill="x", pady=(0, 5))
        
        # Define Grid Weights for Headers
        # Adjusted: ID/Status pinned (weight=0), Title expands (weight=1), Channel/Actions pinned (weight=0)
        headers_frame.columnconfigure(0, weight=0, minsize=120) # ID
        headers_frame.columnconfigure(1, weight=0, minsize=100) # Status
        headers_frame.columnconfigure(2, weight=1)              # Title (Expands)
        headers_frame.columnconfigure(3, weight=0, minsize=150) # Channel
        headers_frame.columnconfigure(4, weight=0, minsize=200) # Actions

        cols = ["ID", "Status", "Title", "Channel", "Actions"]
        for i, col in enumerate(cols):
            lbl = ttk.Label(headers_frame, text=col, font=("Arial", 10, "bold"))
            lbl.grid(row=0, column=i, sticky="w", padx=5)

        # Scrollable List
        self.list_frame = ScrollableFrame(mid_frame)
        self.list_frame.pack(fill="both", expand=True)
        
        # Configure inner frame columns to match headers
        self.list_frame.scrollable_frame.columnconfigure(0, weight=0, minsize=120)
        self.list_frame.scrollable_frame.columnconfigure(1, weight=0, minsize=100)
        self.list_frame.scrollable_frame.columnconfigure(2, weight=1)
        self.list_frame.scrollable_frame.columnconfigure(3, weight=0, minsize=150)
        self.list_frame.scrollable_frame.columnconfigure(4, weight=0, minsize=200)

        # Bottom Frame
        bot_frame = ttk.Frame(self, padding=10)
        bot_frame.pack(fill="x")

        refresh_btn = ttk.Button(bot_frame, text="Refresh", command=self.refresh_table)
        refresh_btn.pack(side="left", padx=5)

        db_btn = ttk.Button(bot_frame, text="Open DB", command=self.open_db)
        db_btn.pack(side="left", padx=5)

        tree_new_btn = ttk.Button(bot_frame, text="Tree New", command=self.open_treesize_new)
        tree_new_btn.pack(side="left", padx=5)

        tree_archive_btn = ttk.Button(bot_frame, text="Tree Archive", command=self.open_treesize_archive)
        tree_archive_btn.pack(side="left", padx=5)

    def add_video(self):
        url = self.url_var.get().strip()
        if url:
            self.app_logic.add_video(url)
            self.url_var.set("")
            self.after(100, self.refresh_table)

    def refresh_table(self):
        # Clear existing
        for widget in self.list_frame.scrollable_frame.winfo_children():
            widget.destroy()

        videos = self.app_logic.get_all_videos()
        
        # Filter videos based on requirements (new, open, down, error)
        allowed_statuses = {'new', 'open', 'down', 'error'}
        active_videos = [v for v in videos if v['status'] in allowed_statuses]
        
        # Grid Layout for rows
        for i, video in enumerate(active_videos):
            row = i
            # ID
            ttk.Label(self.list_frame.scrollable_frame, text=str(video['video_id'])).grid(row=row, column=0, sticky="w", padx=5, pady=5)
            # Status
            status = video['status']
            if video['error_msg']:
                status += " (!)"
            ttk.Label(self.list_frame.scrollable_frame, text=status).grid(row=row, column=1, sticky="w", padx=5, pady=5)
            # Title
            title = video['title'] or ""
            if len(title) > 100:
                title = title[:97] + "..."
            ttk.Label(self.list_frame.scrollable_frame, text=title).grid(row=row, column=2, sticky="w", padx=5, pady=5)
            # Channel
            channel = video['channel'] or ""
            if len(channel) > 20:
                channel = channel[:17] + "..."
            ttk.Label(self.list_frame.scrollable_frame, text=channel).grid(row=row, column=3, sticky="w", padx=5, pady=5)
            
            # Actions Frame
            actions_frame = ttk.Frame(self.list_frame.scrollable_frame)
            actions_frame.grid(row=row, column=4, sticky="w", padx=5, pady=5)
            
            ttk.Button(actions_frame, text="Play", command=lambda v=video['id']: self.app_logic.play_video(v), width=6).pack(side="left", padx=2)
            ttk.Button(actions_frame, text="Del", command=lambda v=video['id']: self.delete_video(v), width=6).pack(side="left", padx=2)
            ttk.Button(actions_frame, text="Archive", command=lambda v=video['id']: self.archive_video(v), width=8).pack(side="left", padx=2)
            ttk.Button(actions_frame, text="Web", command=lambda v=video['id']: self.app_logic.open_web_url(v), width=6).pack(side="left", padx=2)

    def delete_video(self, video_id):
        if messagebox.askyesno("Confirm", "Delete this video?"):
            self.app_logic.delete_video(video_id)
            self.refresh_table()

    def archive_video(self, video_id):
        self.app_logic.archive_video(video_id)
        self.refresh_table()

    def open_db(self):
        self.app_logic.open_db_browser()

    def open_treesize_new(self):
        self.app_logic.open_treesize_new()

    def open_treesize_archive(self):
        self.app_logic.open_treesize_archive()

