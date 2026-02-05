import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import json
import threading
from datetime import datetime

# Import các module chức năng
from api_client import LMStudioClient
from video_downloader import VideoDownloader
from image_generator import ImageGenerator
from srt_translator import SRTTranslator
from story_editor import StoryEditor

class MainApp(ctk.CTk):
    def __init__(self, config):
        super().__init__()
        
        self.config = config
        self.setup_app()
        self.create_widgets()
        self.setup_clients()
        
    def setup_app(self):
        """Cấu hình cửa sổ ứng dụng"""
        self.title(self.config['app_name'])
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Đặt icon
        icon_path = Path(__file__).parent / 'assets' / 'icon.ico'
        if icon_path.exists():
            self.iconbitmap(str(icon_path))
        
        # Chế độ theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Tạo grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
    def setup_clients(self):
        """Khởi tạo các client API"""
        self.lm_client = LMStudioClient(self.config['lm_studio_url'])
        self.video_dl = VideoDownloader()
        self.image_gen = ImageGenerator(self.config['sd_api_url'])
        self.translator = SRTTranslator(self.lm_client)
        self.editor = StoryEditor(self.lm_client)
        
    def create_widgets(self):
        """Tạo tất cả widget giao diện"""
        # Sidebar
        self.create_sidebar()
        
        # Main content area với tabview
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Title bar
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="AI Story Creator Pro",
            font=("Arial", 24, "bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Tabview cho các chức năng
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Tạo 5 tab
        self.tabs = {}
        tab_names = [
            "Chỉnh Sửa Truyện",
            "Dịch Phụ Đề", 
            "Tải Video",
            "Viết Kịch Bản Ảnh",
            "Tạo Ảnh từ Kịch Bản"
        ]
        
        for name in tab_names:
            self.tabs[name] = self.tabview.add(name)
            self.tabview.tab(name).grid_columnconfigure(0, weight=1)
        
        # Tạo nội dung cho từng tab
        self.create_tab1_content()  # Chỉnh sửa truyện
        self.create_tab2_content()  # Dịch phụ đề
        self.create_tab3_content()  # Tải video
        self.create_tab4_content()  # Viết kịch bản ảnh
        self.create_tab5_content()  # Tạo ảnh
        
        # Status bar
        self.create_status_bar()
        
    def create_sidebar(self):
        """Tạo sidebar với logo và navigation"""
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Logo
        logo_path = Path(__file__).parent / 'assets' / 'logo.png'
        if logo_path.exists():
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((150, 150), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = ctk.CTkLabel(sidebar, image=self.logo_photo, text="")
            logo_label.pack(pady=20)
        
        # App name
        app_name_label = ctk.CTkLabel(
            sidebar, 
            text=self.config['app_name'],
            font=("Arial", 16, "bold")
        )
        app_name_label.pack(pady=(0, 30))
        
        # Navigation buttons
        nav_buttons = [
            ("📝 Chỉnh Sửa Truyện", self.show_tab1),
            ("🔤 Dịch Phụ Đề", self.show_tab2),
            ("⬇️ Tải Video", self.show_tab3),
            ("🎬 Viết Kịch Bản", self.show_tab4),
            ("🖼️ Tạo Ảnh", self.show_tab5),
            ("⚙️ Cài Đặt", self.open_settings),
            ("📊 Trạng Thái", self.open_status)
        ]
        
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=command,
                height=40,
                corner_radius=10,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray70", "gray30")
            )
            btn.pack(fill="x", padx=10, pady=5)
        
        # Version info
        version_label = ctk.CTkLabel(
            sidebar,
            text=f"Version: {self.config['version']}",
            font=("Arial", 10)
        )
        version_label.pack(side="bottom", pady=10)
        
    def create_tab1_content(self):
        """Tab 1: Chỉnh sửa truyện"""
        tab = self.tabs["Chỉnh Sửa Truyện"]
        
        # Input frame
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Text input
        ctk.CTkLabel(input_frame, text="Nhập nội dung truyện thô:", font=("Arial", 14)).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.story_text = scrolledtext.ScrolledText(
            input_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            height=15
        )
        self.story_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Options frame
        options_frame = ctk.CTkFrame(input_frame)
        options_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Loại chỉnh sửa
        ctk.CTkLabel(options_frame, text="Loại chỉnh sửa:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.edit_type = ctk.CTkComboBox(
            options_frame,
            values=["Chỉnh văn phong", "Tóm tắt", "Mở rộng", "Sửa lỗi chính tả", "Tối ưu hóa"]
        )
        self.edit_type.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Độ dài output
        ctk.CTkLabel(options_frame, text="Độ dài:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
        self.length_var = tk.StringVar(value="giữ nguyên")
        length_combo = ctk.CTkComboBox(
            options_frame,
            variable=self.length_var,
            values=["giữ nguyên", "ngắn hơn", "dài hơn"]
        )
        length_combo.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        options_frame.grid_columnconfigure(1, weight=1)
        options_frame.grid_columnconfigure(3, weight=1)
        
        # Button frame
        button_frame = ctk.CTkFrame(input_frame)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="Tải File TXT",
            command=self.load_story_file,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Xóa Nội Dung",
            command=self.clear_story_text,
            width=120,
            fg_color="gray",
            hover_color="darkgray"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="🔍 Chỉnh Sửa với AI",
            command=self.process_story_edit,
            width=150,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(side="right", padx=5)
        
        # Output frame
        output_frame = ctk.CTkFrame(tab)
        output_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        ctk.CTkLabel(output_frame, text="Kết quả chỉnh sửa:", font=("Arial", 14)).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.result_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            height=15,
            state="normal"
        )
        self.result_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Save button
        ctk.CTkButton(
            output_frame,
            text="💾 Lưu Kết Quả",
            command=self.save_edited_story,
            width=150
        ).pack(side="right", padx=10, pady=(0, 10))
    
    def create_tab2_content(self):
        """Tab 2: Dịch file SRT"""
        tab = self.tabs["Dịch Phụ Đề"]
        
        # Top frame for file selection
        top_frame = ctk.CTkFrame(tab)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        # File selection
        file_frame = ctk.CTkFrame(top_frame)
        file_frame.pack(fill="x", padx=10, pady=10)
        
        self.srt_file_path = tk.StringVar()
        ctk.CTkEntry(
            file_frame,
            textvariable=self.srt_file_path,
            placeholder_text="Đường dẫn file SRT...",
            width=400
        ).pack(side="left", padx=(0, 10), pady=5, fill="x", expand=True)
        
        ctk.CTkButton(
            file_frame,
            text="📂 Chọn File",
            command=self.select_srt_file,
            width=100
        ).pack(side="right", padx=5, pady=5)
        
        # Translation options
        options_frame = ctk.CTkFrame(top_frame)
        options_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Source language
        ctk.CTkLabel(options_frame, text="Ngôn ngữ gốc:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.src_lang = ctk.CTkComboBox(
            options_frame,
            values=["zh", "en", "ja", "ko", "vi", "auto"]
        )
        self.src_lang.set("auto")
        self.src_lang.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Target language
        ctk.CTkLabel(options_frame, text="Ngôn ngữ đích:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
        self.tgt_lang = ctk.CTkComboBox(
            options_frame,
            values=["vi", "en", "zh", "ja", "ko"]
        )
        self.tgt_lang.set("vi")
        self.tgt_lang.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Translation style
        ctk.CTkLabel(options_frame, text="Văn phong:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.trans_style = ctk.CTkComboBox(
            options_frame,
            values=self.config['translation_styles']
        )
        self.trans_style.set("hiện đại")
        self.trans_style.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Batch size
        ctk.CTkLabel(options_frame, text="Số câu/batch:").grid(row=1, column=2, padx=(20, 5), pady=5, sticky="w")
        self.batch_size = ctk.CTkEntry(options_frame, width=80)
        self.batch_size.insert(0, "10")
        self.batch_size.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        options_frame.grid_columnconfigure(1, weight=1)
        options_frame.grid_columnconfigure(3, weight=0)
        
        # Button frame
        button_frame = ctk.CTkFrame(top_frame)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="🔄 Dịch File SRT",
            command=self.translate_srt_file,
            width=150,
            fg_color="#2196F3",
            hover_color="#1976D2"
        ).pack(side="right", padx=5, pady=5)
        
        # Progress frame
        self.progress_frame = ctk.CTkFrame(tab)
        self.progress_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Sẵn sàng...")
        self.progress_label.pack(padx=10, pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 10))
        self.progress_bar.set(0)
        
        # Preview frame
        preview_frame = ctk.CTkFrame(tab)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Split view for original and translated
        split_frame = ctk.CTkFrame(preview_frame)
        split_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Original text
        orig_frame = ctk.CTkFrame(split_frame)
        orig_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        ctk.CTkLabel(orig_frame, text="Bản gốc:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.orig_text = scrolledtext.ScrolledText(
            orig_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            height=10
        )
        self.orig_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Translated text
        trans_frame = ctk.CTkFrame(split_frame)
        trans_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        ctk.CTkLabel(trans_frame, text="Bản dịch:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.trans_text = scrolledtext.ScrolledText(
            trans_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            height=10
        )
        self.trans_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def create_tab3_content(self):
        """Tab 3: Tải video từ các nền tảng"""
        tab = self.tabs["Tải Video"]
        
        # URL input frame
        url_frame = ctk.CTkFrame(tab)
        url_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(url_frame, text="URL Video:", font=("Arial", 14)).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.video_url = ctk.CTkEntry(
            url_frame,
            placeholder_text="Dán link video từ Bilibili, Tencent, Youku...",
            height=40
        )
        self.video_url.pack(fill="x", padx=10, pady=(0, 10))
        
        # Platform detection
        platform_frame = ctk.CTkFrame(url_frame)
        platform_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(platform_frame, text="Nền tảng hỗ trợ:").pack(side="left", padx=(0, 10))
        
        platforms = self.config['platforms']
        for i in range(0, len(platforms), 3):
            row_frame = ctk.CTkFrame(platform_frame)
            row_frame.pack(fill="x", pady=2)
            
            for j in range(3):
                idx = i + j
                if idx < len(platforms):
                    ctk.CTkLabel(
                        row_frame, 
                        text=f"• {platforms[idx]}",
                        font=("Arial", 10)
                    ).pack(side="left", padx=10)
        
        # Download options
        options_frame = ctk.CTkFrame(tab)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        # Quality selection
        ctk.CTkLabel(options_frame, text="Chất lượng:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.quality = ctk.CTkComboBox(
            options_frame,
            values=["best", "1080p", "720p", "480p", "360p", "worst"]
        )
        self.quality.set("best")
        self.quality.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Format selection
        ctk.CTkLabel(options_frame, text="Định dạng:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
        self.format_var = tk.StringVar(value="mp4")
        format_combo = ctk.CTkComboBox(
            options_frame,
            variable=self.format_var,
            values=["mp4", "mkv", "webm", "flv"]
        )
        format_combo.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Subtitle option
        self.subtitle_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="Tải phụ đề (nếu có)",
            variable=self.subtitle_var
        ).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Audio only option
        self.audio_only_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            options_frame,
            text="Chỉ tải audio",
            variable=self.audio_only_var
        ).grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="w")
        
        options_frame.grid_columnconfigure(1, weight=1)
        options_frame.grid_columnconfigure(3, weight=1)
        
        # Download location
        location_frame = ctk.CTkFrame(tab)
        location_frame.pack(fill="x", padx=10, pady=10)
        
        self.download_path = tk.StringVar(value=str(Path.home() / "Downloads"))
        ctk.CTkLabel(location_frame, text="Lưu tại:").pack(side="left", padx=(10, 5), pady=10)
        
        path_entry = ctk.CTkEntry(
            location_frame,
            textvariable=self.download_path,
            width=300
        )
        path_entry.pack(side="left", padx=5, pady=10, fill="x", expand=True)
        
        ctk.CTkButton(
            location_frame,
            text="📁 Chọn Thư Mục",
            command=self.select_download_folder,
            width=120
        ).pack(side="right", padx=10, pady=10)
        
        # Control buttons
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            control_frame,
            text="🔍 Kiểm Tra URL",
            command=self.check_video_url,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            control_frame,
            text="❌ Xóa URL",
            command=self.clear_video_url,
            width=120,
            fg_color="gray",
            hover_color="darkgray"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            control_frame,
            text="⬇️ Tải Video Ngay",
            command=self.download_video,
            width=150,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(side="right", padx=5)
        
        # Download status
        status_frame = ctk.CTkFrame(tab)
        status_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        ctk.CTkLabel(status_frame, text="Trạng thái tải:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.download_status = scrolledtext.ScrolledText(
            status_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=15
        )
        self.download_status.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Progress bar for download
        self.download_progress = ctk.CTkProgressBar(status_frame)
        self.download_progress.pack(fill="x", padx=10, pady=(0, 10))
        self.download_progress.set(0)
    
    def create_tab4_content(self):
        """Tab 4: Viết kịch bản tạo ảnh từ nội dung truyện"""
        tab = self.tabs["Viết Kịch Bản Ảnh"]
        
        # Input story frame
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(input_frame, text="Nội dung truyện:", font=("Arial", 14)).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.script_story_text = scrolledtext.ScrolledText(
            input_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            height=10
        )
        self.script_story_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Script options
        options_frame = ctk.CTkFrame(input_frame)
        options_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Style selection
        ctk.CTkLabel(options_frame, text="Phong cách ảnh:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.image_style = ctk.CTkComboBox(
            options_frame,
            values=["anime", "realistic", "painting", "digital art", "fantasy", "cinematic"]
        )
        self.image_style.set("anime")
        self.image_style.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Number of scenes
        ctk.CTkLabel(options_frame, text="Số cảnh:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
        self.num_scenes = ctk.CTkEntry(options_frame, width=80)
        self.num_scenes.insert(0, "5")
        self.num_scenes.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # Detail level
        ctk.CTkLabel(options_frame, text="Mức độ chi tiết:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.detail_level = ctk.CTkComboBox(
            options_frame,
            values=["cơ bản", "chi tiết", "rất chi tiết"]
        )
        self.detail_level.set("chi tiết")
        self.detail_level.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Include prompts
        self.include_prompts = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="Bao gồm prompt cho AI",
            variable=self.include_prompts
        ).grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="w")
        
        options_frame.grid_columnconfigure(1, weight=1)
        options_frame.grid_columnconfigure(3, weight=0)
        
        # Button frame
        button_frame = ctk.CTkFrame(input_frame)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="📝 Tạo Kịch Bản Ảnh",
            command=self.generate_image_script,
            width=150,
            fg_color="#9C27B0",
            hover_color="#7B1FA2"
        ).pack(side="right", padx=5)
        
        # Script output
        output_frame = ctk.CTkFrame(tab)
        output_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        ctk.CTkLabel(output_frame, text="Kịch bản ảnh:", font=("Arial", 14)).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.script_output = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=15
        )
        self.script_output.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Export buttons
        export_frame = ctk.CTkFrame(output_frame)
        export_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            export_frame,
            text="💾 Lưu Kịch Bản",
            command=self.save_image_script,
            width=120
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            export_frame,
            text="📋 Sao Chép",
            command=self.copy_script_to_clipboard,
            width=120
        ).pack(side="right", padx=5)
    
    def create_tab5_content(self):
        """Tab 5: Tạo ảnh từ kịch bản"""
        tab = self.tabs["Tạo Ảnh từ Kịch Bản"]
        
        # Script input frame
        script_frame = ctk.CTkFrame(tab)
        script_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(script_frame, text="Nhập prompt hoặc kịch bản ảnh:", font=("Arial", 14)).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.image_prompt_text = scrolledtext.ScrolledText(
            script_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            height=8
        )
        self.image_prompt_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Load script button
        ctk.CTkButton(
            script_frame,
            text="📂 Tải Kịch Bản từ File",
            command=self.load_image_script,
            width=150
        ).pack(side="right", padx=10, pady=(0, 10))
        
        # Image generation options
        options_frame = ctk.CTkFrame(tab)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        # Model selection
        ctk.CTkLabel(options_frame, text="Model AI:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.image_model = ctk.CTkComboBox(
            options_frame,
            values=["stable-diffusion", "midjourney-style", "anime-diffusion", "realistic-vision"]
        )
        self.image_model.set("stable-diffusion")
        self.image_model.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Image size
        ctk.CTkLabel(options_frame, text="Kích thước:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
        self.image_size = ctk.CTkComboBox(
            options_frame,
            values=["512x512", "768x768", "1024x1024", "512x768", "768x512"]
        )
        self.image_size.set("512x512")
        self.image_size.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Number of images
        ctk.CTkLabel(options_frame, text="Số ảnh:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.num_images = ctk.CTkEntry(options_frame, width=80)
        self.num_images.insert(0, "1")
        self.num_images.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Steps
        ctk.CTkLabel(options_frame, text="Số steps:").grid(row=1, column=2, padx=(20, 5), pady=5, sticky="w")
        self.steps = ctk.CTkEntry(options_frame, width=80)
        self.steps.insert(0, "30")
        self.steps.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # CFG scale
        ctk.CTkLabel(options_frame, text="CFG Scale:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.cfg_scale = ctk.CTkEntry(options_frame, width=80)
        self.cfg_scale.insert(0, "7.5")
        self.cfg_scale.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Sampler
        ctk.CTkLabel(options_frame, text="Sampler:").grid(row=2, column=2, padx=(20, 5), pady=5, sticky="w")
        self.sampler = ctk.CTkComboBox(
            options_frame,
            values=["Euler a", "DPM++ 2M", "DDIM", "LMS", "Heun"]
        )
        self.sampler.set("Euler a")
        self.sampler.grid(row=2, column=3, padx=5, pady=5, sticky="ew")
        
        options_frame.grid_columnconfigure(1, weight=1)
        options_frame.grid_columnconfigure(3, weight=1)
        
        # Generate button
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="🖼️ Tạo Ảnh Ngay",
            command=self.generate_images,
            width=150,
            fg_color="#FF9800",
            hover_color="#F57C00"
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="🔄 Tạo Batch",
            command=self.generate_batch_images,
            width=120
        ).pack(side="right", padx=5)
        
        # Image preview area
        preview_frame = ctk.CTkFrame(tab)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        ctk.CTkLabel(preview_frame, text="Xem trước ảnh:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Canvas for image display
        self.image_canvas = tk.Canvas(
            preview_frame,
            bg="#2B2B2B",
            highlightthickness=0
        )
        self.image_canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Image controls
        control_frame = ctk.CTkFrame(preview_frame)
        control_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            control_frame,
            text="📂 Mở Thư Mục Ảnh",
            command=self.open_image_folder,
            width=140
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            control_frame,
            text="⬇️ Tải Ảnh Xuống",
            command=self.download_generated_image,
            width=140
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            control_frame,
            text="🗑️ Xóa Ảnh",
            command=self.clear_generated_image,
            width=100,
            fg_color="gray",
            hover_color="darkgray"
        ).pack(side="right", padx=5)
    
    def create_status_bar(self):
        """Tạo status bar ở dưới cùng"""
        self.status_bar = ctk.CTkFrame(self, height=30)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_bar.grid_propagate(False)
        
        # Left status
        self.left_status = ctk.CTkLabel(
            self.status_bar,
            text="Sẵn sàng",
            font=("Arial", 10)
        )
        self.left_status.pack(side="left", padx=10, pady=5)
        
        # Center status (LM Studio connection)
        self.center_status = ctk.CTkLabel(
            self.status_bar,
            text="LM Studio: Đang kiểm tra...",
            font=("Arial", 10)
        )
        self.center_status.pack(side="left", padx=20, pady=5)
        
        # Right status (memory usage)
        self.right_status = ctk.CTkLabel(
            self.status_bar,
            text="Bộ nhớ: --",
            font=("Arial", 10)
        )
        self.right_status.pack(side="right", padx=10, pady=5)
        
        # Start checking connection
        self.check_lm_studio_connection()
    
    def check_lm_studio_connection(self):
        """Kiểm tra kết nối đến LM Studio"""
        def check():
            try:
                if self.lm_client.check_connection():
                    self.center_status.configure(
                        text="LM Studio: Đã kết nối ✅",
                        text_color="green"
                    )
                else:
                    self.center_status.configure(
                        text="LM Studio: Chưa kết nối ❌",
                        text_color="red"
                    )
            except:
                self.center_status.configure(
                    text="LM Studio: Lỗi kết nối",
                    text_color="orange"
                )
        
        threading.Thread(target=check, daemon=True).start()
    
    # ====== CÁC HÀM XỬ LÝ SỰ KIỆN ======
    
    def show_tab1(self):
        """Hiển thị tab 1"""
        self.tabview.set("Chỉnh Sửa Truyện")
    
    def show_tab2(self):
        """Hiển thị tab 2"""
        self.tabview.set("Dịch Phụ Đề")
    
    def show_tab3(self):
        """Hiển thị tab 3"""
        self.tabview.set("Tải Video")
    
    def show_tab4(self):
        """Hiển thị tab 4"""
        self.tabview.set("Viết Kịch Bản Ảnh")
    
    def show_tab5(self):
        """Hiển thị tab 5"""
        self.tabview.set("Tạo Ảnh từ Kịch Bản")
    
    def open_settings(self):
        """Mở cửa sổ cài đặt"""
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Cài Đặt Ứng Dụng")
        settings_window.geometry("600x400")
        settings_window.transient(self)
        settings_window.grab_set()
        
        # Tabview for settings
        settings_tabview = ctk.CTkTabview(settings_window)
        settings_tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # General settings tab
        general_tab = settings_tabview.add("Chung")
        
        # AI settings tab
        ai_tab = settings_tabview.add("AI")
        
        # Path settings tab
        path_tab = settings_tabview.add("Đường Dẫn")
        
        # TODO: Thêm nội dung cho các tab settings
        
        # Close button
        ctk.CTkButton(
            settings_window,
            text="Đóng",
            command=settings_window.destroy
        ).pack(pady=10)
    
    def open_status(self):
        """Mở cửa sổ trạng thái hệ thống"""
        status_window = ctk.CTkToplevel(self)
        status_window.title("Trạng Thái Hệ Thống")
        status_window.geometry("500x300")
        status_window.transient(self)
        
        # Add status information
        # TODO: Thêm thông tin trạng thái chi tiết
        
        ctk.CTkLabel(
            status_window,
            text="Thông tin hệ thống sẽ được hiển thị ở đây",
            font=("Arial", 12)
        ).pack(expand=True)
        
    def load_story_file(self):
        """Tải file truyện từ hệ thống"""
        file_path = filedialog.askopenfilename(
            title="Chọn file truyện",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.story_text.delete(1.0, tk.END)
                self.story_text.insert(1.0, content)
                self.update_status(f"Đã tải file: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc file: {str(e)}")
    
    def clear_story_text(self):
        """Xóa nội dung truyện"""
        self.story_text.delete(1.0, tk.END)
    
    def process_story_edit(self):
        """Xử lý chỉnh sửa truyện với AI"""
        story = self.story_text.get(1.0, tk.END).strip()
        if not story:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập nội dung truyện!")
            return
        
        edit_type = self.edit_type.get()
        length_pref = self.length_var.get()
        
        # Hiển thị trạng thái xử lý
        self.update_status(f"Đang xử lý với AI ({edit_type})...")
        
        def process():
            try:
                # Gọi API LM Studio
                result = self.editor.edit_story(
                    story=story,
                    edit_type=edit_type,
                    length_preference=length_pref
                )
                
                # Cập nhật UI trong main thread
                self.after(0, lambda: self.show_edit_result(result))
                
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(
                    "Lỗi", 
                    f"Không thể xử lý truyện: {str(e)}"
                ))
        
        # Chạy trong thread riêng
        threading.Thread(target=process, daemon=True).start()
    
    def show_edit_result(self, result):
        """Hiển thị kết quả chỉnh sửa"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, result)
        self.update_status("Đã hoàn thành chỉnh sửa!")
    
    def save_edited_story(self):
        """Lưu kết quả chỉnh sửa"""
        content = self.result_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Cảnh báo", "Không có nội dung để lưu!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Lưu truyện đã chỉnh sửa",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.update_status(f"Đã lưu file: {os.path.basename(file_path)}")
                messagebox.showinfo("Thành công", "Đã lưu truyện thành công!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {str(e)}")
    
    def select_srt_file(self):
        """Chọn file SRT"""
        file_path = filedialog.askopenfilename(
            title="Chọn file SRT",
            filetypes=[("SRT files", "*.srt"), ("All files", "*.*")]
        )
        
        if file_path:
            self.srt_file_path.set(file_path)
            self.load_srt_preview(file_path)
    
    def load_srt_preview(self, file_path):
        """Tải preview của file SRT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Hiển thị 10 dòng đầu tiên
            lines = content.split('\n')[:30]
            preview = '\n'.join(lines)
            
            self.orig_text.delete(1.0, tk.END)
            self.orig_text.insert(1.0, preview)
            
            self.update_status(f"Đã tải file SRT: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file SRT: {str(e)}")
    
    def translate_srt_file(self):
        """Dịch file SRT"""
        file_path = self.srt_file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file SRT!")
            return
        
        src_lang = self.src_lang.get()
        tgt_lang = self.tgt_lang.get()
        style = self.trans_style.get()
        
        try:
            batch_size = int(self.batch_size.get())
        except:
            batch_size = 10
        
        self.update_status("Đang bắt đầu dịch...")
        self.progress_bar.set(0)
        
        def translate():
            try:
                # Dịch file SRT
                result = self.translator.translate_file(
                    file_path=file_path,
                    src_lang=src_lang,
                    tgt_lang=tgt_lang,
                    style=style,
                    batch_size=batch_size,
                    progress_callback=self.update_translation_progress
                )
                
                # Hiển thị kết quả
                self.after(0, lambda: self.show_translation_result(result, file_path))
                
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(
                    "Lỗi", 
                    f"Lỗi khi dịch: {str(e)}"
                ))
        
        threading.Thread(target=translate, daemon=True).start()
    
    def update_translation_progress(self, current, total):
        """Cập nhật tiến trình dịch"""
        progress = current / total if total > 0 else 0
        
        def update():
            self.progress_bar.set(progress)
            self.progress_label.configure(
                text=f"Đang dịch... {current}/{total} câu ({progress*100:.1f}%)"
            )
        
        self.after(0, update)
    
    def show_translation_result(self, result, original_path):
        """Hiển thị kết quả dịch"""
        # Hiển thị preview
        self.trans_text.delete(1.0, tk.END)
        self.trans_text.insert(1.0, result[:5000])  # Giới hạn preview
        
        # Hỏi người dùng có muốn lưu không
        save = messagebox.askyesno(
            "Thành công", 
            f"Đã dịch xong! Bạn có muốn lưu file không?"
        )
        
        if save:
            # Tạo tên file mới
            dir_name = os.path.dirname(original_path)
            base_name = os.path.basename(original_path)
            name, ext = os.path.splitext(base_name)
            new_name = f"{name}_translated{ext}"
            save_path = os.path.join(dir_name, new_name)
            
            # Lưu file
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(result)
                
                self.update_status(f"Đã lưu file dịch: {new_name}")
                messagebox.showinfo("Thành công", f"Đã lưu file: {new_name}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {str(e)}")
        
        self.progress_label.configure(text="Hoàn thành!")
        self.progress_bar.set(1)
    
    def select_download_folder(self):
        """Chọn thư mục download"""
        folder = filedialog.askdirectory(title="Chọn thư mục lưu video")
        if folder:
            self.download_path.set(folder)
    
    def check_video_url(self):
        """Kiểm tra URL video"""
        url = self.video_url.get().strip()
        if not url:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập URL video!")
            return
        
        self.update_status(f"Đang kiểm tra URL: {url[:50]}...")
        
        def check():
            try:
                info = self.video_dl.get_video_info(url)
                
                # Hiển thị thông tin video
                info_text = f"Tìm thấy video:\n"
                info_text += f"Tiêu đề: {info.get('title', 'Không rõ')}\n"
                info_text += f"Thời lượng: {info.get('duration', 0)} giây\n"
                info_text += f"Định dạng: {info.get('ext', 'Không rõ')}\n"
                info_text += f"Chất lượng có sẵn: {', '.join(info.get('formats', []))}\n"
                
                self.after(0, lambda: self.show_video_info(info_text))
                
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(
                    "Lỗi", 
                    f"Không thể kiểm tra URL: {str(e)}"
                ))
        
        threading.Thread(target=check, daemon=True).start()
    
    def show_video_info(self, info):
        """Hiển thị thông tin video"""
        self.download_status.delete(1.0, tk.END)
        self.download_status.insert(1.0, info)
        self.update_status("Đã kiểm tra URL thành công!")
    
    def clear_video_url(self):
        """Xóa URL video"""
        self.video_url.delete(0, tk.END)
        self.download_status.delete(1.0, tk.END)
    
    def download_video(self):
        """Tải video"""
        url = self.video_url.get().strip()
        if not url:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập URL video!")
            return
        
        quality = self.quality.get()
        fmt = self.format_var.get()
        download_path = self.download_path.get()
        subtitle = self.subtitle_var.get()
        audio_only = self.audio_only_var.get()
        
        self.update_status(f"Đang bắt đầu tải video...")
        self.download_progress.set(0)
        
        def download():
            try:
                # Tải video với progress callback
                result = self.video_dl.download(
                    url=url,
                    quality=quality,
                    output_format=fmt,
                    output_path=download_path,
                    subtitles=subtitle,
                    audio_only=audio_only,
                    progress_callback=self.update_download_progress,
                    status_callback=self.update_download_status
                )
                
                self.after(0, lambda: self.download_complete(result))
                
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(
                    "Lỗi", 
                    f"Lỗi khi tải video: {str(e)}"
                ))
        
        threading.Thread(target=download, daemon=True).start()
    
    def update_download_progress(self, percent):
        """Cập nhật tiến trình download"""
        def update():
            self.download_progress.set(percent / 100)
        
        self.after(0, update)
    
    def update_download_status(self, status):
        """Cập nhật trạng thái download"""
        def update():
            self.download_status.insert(tk.END, status + "\n")
            self.download_status.see(tk.END)
        
        self.after(0, update)
    
    def download_complete(self, result):
        """Xử lý khi download hoàn thành"""
        self.download_progress.set(1)
        self.update_status(f"Đã tải video: {os.path.basename(result)}")
        messagebox.showinfo("Thành công", f"Đã tải video thành công!\nLưu tại: {result}")
    
    def generate_image_script(self):
        """Tạo kịch bản ảnh từ truyện"""
        story = self.script_story_text.get(1.0, tk.END).strip()
        if not story:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập nội dung truyện!")
            return
        
        style = self.image_style.get()
        
        try:
            num_scenes = int(self.num_scenes.get())
        except:
            num_scenes = 5
        
        detail = self.detail_level.get()
        include_prompts = self.include_prompts.get()
        
        self.update_status("Đang tạo kịch bản ảnh với AI...")
        
        def generate():
            try:
                # Gọi API để tạo kịch bản
                script = self.editor.generate_image_script(
                    story=story,
                    num_scenes=num_scenes,
                    style=style,
                    detail_level=detail,
                    include_prompts=include_prompts
                )
                
                self.after(0, lambda: self.show_generated_script(script))
                
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(
                    "Lỗi", 
                    f"Không thể tạo kịch bản: {str(e)}"
                ))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def show_generated_script(self, script):
        """Hiển thị kịch bản đã tạo"""
        self.script_output.delete(1.0, tk.END)
        self.script_output.insert(1.0, script)
        self.update_status("Đã tạo kịch bản ảnh!")
    
    def save_image_script(self):
        """Lưu kịch bản ảnh"""
        content = self.script_output.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Cảnh báo", "Không có kịch bản để lưu!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Lưu kịch bản ảnh",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.update_status(f"Đã lưu kịch bản: {os.path.basename(file_path)}")
                messagebox.showinfo("Thành công", "Đã lưu kịch bản thành công!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {str(e)}")
    
    def copy_script_to_clipboard(self):
        """Sao chép kịch bản vào clipboard"""
        content = self.script_output.get(1.0, tk.END).strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.update_status("Đã sao chép kịch bản vào clipboard!")
            messagebox.showinfo("Thành công", "Đã sao chép kịch bản!")
        else:
            messagebox.showwarning("Cảnh báo", "Không có nội dung để sao chép!")
    
    def load_image_script(self):
        """Tải kịch bản ảnh từ file"""
        file_path = filedialog.askopenfilename(
            title="Chọn file kịch bản",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.image_prompt_text.delete(1.0, tk.END)
                self.image_prompt_text.insert(1.0, content)
                self.update_status(f"Đã tải kịch bản: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc file: {str(e)}")
    
    def generate_images(self):
        """Tạo ảnh từ prompt"""
        prompt = self.image_prompt_text.get(1.0, tk.END).strip()
        if not prompt:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập prompt hoặc kịch bản!")
            return
        
        model = self.image_model.get()
        size = self.image_size.get()
        
        try:
            num_images = int(self.num_images.get())
            steps = int(self.steps.get())
            cfg_scale = float(self.cfg_scale.get())
        except:
            num_images = 1
            steps = 30
            cfg_scale = 7.5
        
        sampler = self.sampler.get()
        
        self.update_status("Đang tạo ảnh với AI...")
        
        def generate():
            try:
                # Tạo ảnh
                images = self.image_gen.generate(
                    prompt=prompt,
                    model=model,
                    width=int(size.split('x')[0]),
                    height=int(size.split('x')[1]),
                    num_images=num_images,
                    steps=steps,
                    cfg_scale=cfg_scale,
                    sampler=sampler
                )
                
                self.after(0, lambda: self.show_generated_images(images))
                
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(
                    "Lỗi", 
                    f"Không thể tạo ảnh: {str(e)}"
                ))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def generate_batch_images(self):
        """Tạo batch ảnh từ nhiều prompt"""
        # TODO: Implement batch generation
        messagebox.showinfo("Thông tin", "Tính năng đang phát triển!")
    
    def show_generated_images(self, image_paths):
        """Hiển thị ảnh đã tạo"""
        if not image_paths:
            messagebox.showwarning("Cảnh báo", "Không tạo được ảnh nào!")
            return
        
        # Hiển thị ảnh đầu tiên
        first_image = image_paths[0]
        
        try:
            img = Image.open(first_image)
            img.thumbnail((400, 400))
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Clear canvas và hiển thị ảnh mới
            self.image_canvas.delete("all")
            self.image_canvas.create_image(
                200, 200,
                image=photo
            )
            self.image_canvas.image = photo  # Giữ reference
            
            self.update_status(f"Đã tạo {len(image_paths)} ảnh!")
            messagebox.showinfo("Thành công", f"Đã tạo {len(image_paths)} ảnh!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể hiển thị ảnh: {str(e)}")
    
    def open_image_folder(self):
        """Mở thư mục chứa ảnh"""
        output_dir = Path(__file__).parent / 'output' / 'images'
        output_dir.mkdir(exist_ok=True)
        
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                os.startfile(output_dir)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(output_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(output_dir)])
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở thư mục: {str(e)}")
    
    def download_generated_image(self):
        """Tải ảnh đã tạo"""
        # TODO: Implement download image
        messagebox.showinfo("Thông tin", "Tính năng đang phát triển!")
    
    def clear_generated_image(self):
        """Xóa ảnh hiển thị"""
        self.image_canvas.delete("all")
        self.update_status("Đã xóa ảnh hiển thị")
    
    def update_status(self, message):
        """Cập nhật status bar"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.left_status.configure(text=f"[{timestamp}] {message}")
