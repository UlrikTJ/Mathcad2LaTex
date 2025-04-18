#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MathCad to LaTeX Translator GUI
------------------------------
A modern GUI interface for the MathCad to LaTeX translator.
"""

import os
import tempfile
import subprocess
import threading
import platform
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from mathcad_to_latex import convert_mathcad_to_latex

# Import PIL modules at module level
try:
    from PIL import Image, ImageTk
except ImportError:
    # PIL might not be installed, but we'll handle this in the rendering logic
    pass

# Check for LaTeX installation
HAS_LATEX = False
try:
    process = subprocess.run(['pdflatex', '--version'], capture_output=True, timeout=2)
    HAS_LATEX = process.returncode == 0
except (subprocess.SubprocessError, FileNotFoundError):
    pass

# Check for matplotlib
MATPLOTLIB_AVAILABLE = False
try:
    import matplotlib
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    pass

class ModernTheme:
    """Modern theme styling constants for the application."""
    # Colors
    PRIMARY = "#3498db"  # Blue for main elements
    SECONDARY = "#2ecc71"  # Green for secondary elements
    SUCCESS = "#27ae60"  # Darker green for success indicators
    WARNING = "#f39c12"  # Orange for warnings
    ERROR = "#e74c3c"  # Red for errors
    
    # Background colors
    BG_COLOR = "#f5f5f7"  # Light gray with slight blue tint
    BG_DARK = "#e0e0e3"   # Slightly darker background
    CARD_BG = "#ffffff"   # White for card backgrounds
    INPUT_BG = "#ffffff"  # White for input backgrounds
    
    # Text colors
    TEXT = "#212121"      # Nearly black for main text
    TEXT_LIGHT = "#757575"  # Gray for secondary text
    TEXT_FADED = "#9e9e9e"  # Lighter gray for less important text
    BUTTON_TEXT = "#ffffff"  # White for button text, will be adjusted for better contrast
    
    # Sizing and spacing
    PADDING = 10
    BORDER_RADIUS = 8
    
    @classmethod
    def apply_theme(cls, root):
        """Apply the modern theme to the application."""
        style = ttk.Style()
        
        # Configure the basic theme
        if platform.system() == "Windows":
            style.theme_use('vista')
        else:
            style.theme_use('clam')  # More compatible theme for other platforms
        
        # Configure basic elements
        style.configure("TFrame", background=cls.BG_COLOR)
        style.configure("TLabel", background=cls.BG_COLOR, foreground=cls.TEXT)
        style.configure("TButton", 
                       background=cls.PRIMARY, 
                       foreground="#000000",  # Changed to black for better contrast
                       padding=(10, 5))
        
        # Specific styles for different elements
        style.configure("Card.TFrame", 
                       background=cls.CARD_BG, 
                       relief="flat", 
                       borderwidth=0)
        
        style.configure("Header.TLabel", 
                       font=("Segoe UI", 16, "bold"), 
                       foreground=cls.PRIMARY,
                       background=cls.BG_COLOR,
                       padding=5)
        
        style.configure("Subheader.TLabel", 
                       font=("Segoe UI", 12),
                       foreground=cls.TEXT,
                       background=cls.BG_COLOR,
                       padding=3)
        
        # Button styles
        style.configure("Primary.TButton", 
                       background=cls.PRIMARY, 
                       foreground="#000000",  # Changed to black for better contrast
                       padding=(10, 5),
                       font=("Segoe UI", 10, "bold"))
        
        style.configure("Secondary.TButton", 
                       background=cls.SECONDARY, 
                       foreground="#000000",  # Changed to black for better contrast
                       padding=(10, 5),
                       font=("Segoe UI", 10, "bold"))
        
        style.configure("Accent.TButton", 
                       background=cls.WARNING, 
                       foreground="#000000",  # Changed to black for better contrast
                       padding=(10, 5),
                       font=("Segoe UI", 10, "bold"))
        
        style.configure("Outline.TButton", 
                       background="white", 
                       foreground=cls.PRIMARY,
                       padding=(10, 5))
        
        # Configure button hover effects
        style.map("TButton",
                 background=[("active", cls.PRIMARY)],
                 foreground=[("active", "#000000")])  # Changed to black for better contrast
        
        style.map("Primary.TButton",
                 background=[("active", "#2980b9")],  # Darker blue on hover
                 foreground=[("active", "#000000")])  # Changed to black for better contrast
        
        style.map("Secondary.TButton",
                 background=[("active", "#27ae60")],  # Darker green on hover
                 foreground=[("active", "#000000")])  # Changed to black for better contrast
        
        style.map("Accent.TButton",
                 background=[("active", "#f39c12")],  # Darker orange on hover
                 foreground=[("active", "#000000")])  # Changed to black for better contrast
        
        style.map("Outline.TButton",
                 background=[("active", "#f5f5f7")],
                 foreground=[("active", cls.PRIMARY)])
        
        # Configure other elements
        style.configure("TNotebook", 
                       background=cls.BG_COLOR,
                       tabmargins=[2, 5, 2, 0])
        
        style.configure("TNotebook.Tab", 
                       background=cls.BG_DARK,
                       foreground=cls.TEXT,
                       padding=[12, 4],
                       font=("Segoe UI", 9))
        
        style.map("TNotebook.Tab",
                 background=[("selected", cls.CARD_BG)],
                 foreground=[("selected", cls.PRIMARY)],
                 expand=[("selected", [1, 1, 1, 0])])

class MathcadToLatexGUI:
    """GUI application for converting Mathcad expressions to LaTeX."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Mathcad to LaTeX Converter")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Apply modern theme
        ModernTheme.apply_theme(root)
        
        # Configure the root window background
        self.root.configure(bg=ModernTheme.BG_COLOR)
        
        # Initialize drag data and zoom state
        self._drag_data = {"x": 0, "y": 0, "item": None}
        self.current_scale = 1.0
        self.original_image = None
        
        # Create main container with padding
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create the header
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.title_label = ttk.Label(self.header_frame, 
                                   text="Mathcad to LaTeX Converter", 
                                   style="Header.TLabel")
        self.title_label.pack(side=tk.LEFT, pady=5)
        
        # Show status of rendering engines
        self.engine_frame = ttk.Frame(self.header_frame)
        self.engine_frame.pack(side=tk.RIGHT, pady=5)
        
        latex_status = "✓ LaTeX installed" if HAS_LATEX else "✗ LaTeX not detected"
        latex_color = ModernTheme.SUCCESS if HAS_LATEX else ModernTheme.TEXT_LIGHT
        self.latex_status = ttk.Label(self.engine_frame, 
                                    text=latex_status,
                                    foreground=latex_color,
                                    font=("Segoe UI", 9))
        self.latex_status.pack(side=tk.RIGHT, padx=10)
        
        matplotlib_status = "✓ Matplotlib available" if MATPLOTLIB_AVAILABLE else "✗ Matplotlib not detected"
        matplotlib_color = ModernTheme.SUCCESS if MATPLOTLIB_AVAILABLE else ModernTheme.TEXT_LIGHT
        self.matplotlib_status = ttk.Label(self.engine_frame, 
                                         text=matplotlib_status,
                                         foreground=matplotlib_color,
                                         font=("Segoe UI", 9))
        self.matplotlib_status.pack(side=tk.RIGHT, padx=10)
        
        # Create vertical layout for input, output, and preview
        self.vertical_paned_window = ttk.PanedWindow(self.main_frame, orient=tk.VERTICAL)
        self.vertical_paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Create input panel
        self.input_frame = ttk.Frame(self.vertical_paned_window, style="Card.TFrame")
        
        # Create output panel
        self.output_frame = ttk.Frame(self.vertical_paned_window, style="Card.TFrame")
        
        # Create preview panel
        self.preview_frame = ttk.Frame(self.vertical_paned_window, style="Card.TFrame")
        
        # Add frames to the paned window with different weights for improved initial distribution
        self.vertical_paned_window.add(self.input_frame, weight=1)
        self.vertical_paned_window.add(self.output_frame, weight=2)  # Give output twice the weight
        self.vertical_paned_window.add(self.preview_frame, weight=3)  # Give preview three times the weight
        
        # Configure the initial sash positions for better distribution
        self.root.update_idletasks()  # Update to get the correct total height
        total_height = self.vertical_paned_window.winfo_height()
        if total_height > 0:  # Only set positions if we have valid height
            first_sash = total_height // 5  # Make input ~20% of height
            second_sash = int(total_height * 0.6)  # Make output ~40% of height
            self.vertical_paned_window.sashpos(0, first_sash)
            self.vertical_paned_window.sashpos(1, second_sash)
        
        # Store original sash positions
        self.user_adjusted_sashes = False
        
        # Bind paned window sash movements to track when user manually adjusts sizes
        self.vertical_paned_window.bind("<ButtonRelease-1>", self._on_sash_moved)

        # Configure the input section
        self._setup_input_section()
        
        # Configure the output section
        self._setup_output_section()
        
        # Configure the preview section
        self._setup_preview_section()
        
        # Create the footer
        self.footer_frame = ttk.Frame(self.main_frame)
        self.footer_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.app_info_label = ttk.Label(self.footer_frame, 
                                      text="© 2025 Mathcad to LaTeX Converter",
                                      foreground=ModernTheme.TEXT_LIGHT,
                                      font=("Segoe UI", 8))
        self.app_info_label.pack(side=tk.LEFT)
        
        # Initial render
        self._update_preview()
    
    def _setup_input_section(self):
        """Configure the input section with editor and controls."""
        # Input section header
        input_header = ttk.Frame(self.input_frame)
        input_header.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        input_label = ttk.Label(input_header, 
                              text="Mathcad Expression",
                              style="SectionTitle.TLabel")
        input_label.pack(side=tk.LEFT)
        
        # Control buttons
        self.controls_frame = ttk.Frame(input_header)
        self.controls_frame.pack(side=tk.RIGHT)
        
        self.convert_btn = ttk.Button(self.controls_frame, 
                                    text="Convert", 
                                    command=self._convert_expression,
                                    style="Secondary.TButton")
        self.convert_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.clear_btn = ttk.Button(self.controls_frame, 
                                  text="Clear", 
                                  command=self._clear_text,
                                  style="Secondary.TButton")
        self.clear_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.example_btn = ttk.Button(self.controls_frame, 
                                    text="Load Example", 
                                    command=self._load_example,
                                    style="Secondary.TButton")
        self.example_btn.pack(side=tk.RIGHT)
        
        # Input text area with scrollbar in a container
        editor_container = ttk.Frame(self.input_frame)
        editor_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Configure grid layout for proper resizing
        editor_container.columnconfigure(0, weight=1)
        editor_container.rowconfigure(0, weight=1)
        
        # Create a scrollbar
        scrollbar = ttk.Scrollbar(editor_container)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Create the text widget with modern font
        self.input_text = tk.Text(editor_container, 
                                 font=("Consolas", 11),
                                 bg=ModernTheme.INPUT_BG,
                                 fg=ModernTheme.TEXT,
                                 insertbackground=ModernTheme.TEXT,
                                 relief=tk.FLAT,
                                 padx=10,
                                 pady=10,
                                 wrap=tk.WORD,
                                 yscrollcommand=scrollbar.set)
        
        self.input_text.grid(row=0, column=0, sticky='nsew')
        scrollbar.config(command=self.input_text.yview)
        
        # Bind events for real-time preview
        self.input_text.bind("<KeyRelease>", self._on_key_release)
        
        # Add a placeholder
        self.input_text.insert(tk.END, "Enter your Mathcad expression here...")
        self.input_text.bind("<FocusIn>", self._clear_placeholder)
        self.input_text.tag_configure("placeholder", foreground=ModernTheme.TEXT_LIGHT)
        self.input_text.tag_add("placeholder", "1.0", "end")
    
    def _setup_output_section(self):
        """Set up the output section with output field and controls."""
        self.output_label = ttk.Label(self.output_frame, text="LaTeX Output:", style="Subheader.TLabel")
        self.output_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Add output text area with modern styling
        self.output_text = scrolledtext.ScrolledText(self.output_frame, 
                                                  height=8, 
                                                  font=("Consolas", 11),
                                                  bg=ModernTheme.INPUT_BG,
                                                  fg=ModernTheme.TEXT,
                                                  padx=10,
                                                  pady=10)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.bind("<KeyRelease>", lambda event: self._update_preview())
        
        # Bind output text changes to allow automatic resizing
        self.output_text.bind("<<Modified>>", self._on_output_modified)

        # Copy button with secondary style
        self.copy_button = ttk.Button(
            self.output_frame, 
            text="Copy LaTeX", 
            command=self._copy_latex,
            style="Secondary.TButton"
        )
        self.copy_button.pack(anchor=tk.E, pady=5)
        
        # Continue iteration button
        self.continue_button = ttk.Button(
            self.output_frame,
            text="Continue Iteration",
            command=self._continue_iteration,
            style="Accent.TButton"
        )
        self.continue_button.pack(anchor=tk.E, pady=5)
    
    def _setup_preview_section(self):
        """Set up the preview section with a LaTeX preview."""
        self.preview_header = ttk.Label(self.preview_frame, 
                                     text="LaTeX Preview",
                                     style="Subheader.TLabel")
        self.preview_header.pack(anchor=tk.W, pady=(10, 5), padx=10)
        
        # Create a container with specific background color
        self.preview_container = tk.Frame(self.preview_frame, 
                                        background=ModernTheme.CARD_BG,
                                        highlightthickness=1,
                                        highlightbackground=ModernTheme.BG_DARK)
        self.preview_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def _convert_expression(self):
        """Convert Mathcad expression to LaTeX."""
        mathcad_expr = self.input_text.get(1.0, tk.END).strip()
        
        if not mathcad_expr:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "")
            self._update_preview()
            return
        
        try:
            latex_expr = convert_mathcad_to_latex(mathcad_expr)
            
            # Update output field
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, latex_expr)
            
            # Update preview
            self._update_preview()
        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Error: {str(e)}")
            self._update_preview()
    
    def _continue_iteration(self):
        """Continue to the next iteration of LaTeX conversion refinement."""
        # Get current LaTeX from output field
        current_latex = self.output_text.get(1.0, tk.END).strip()
        
        if not current_latex:
            messagebox.showinfo("Information", "No LaTeX to iterate on. Please convert an expression first.")
            return
            
        try:
            # You can define specific iteration rules here
            # For example, simplifying fractions, expanding expressions, etc.
            from mathcad_to_latex import refine_latex
            
            refined_latex = refine_latex(current_latex)
            
            # Update the output with the refined LaTeX
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, refined_latex)
            
            # Update the preview
            self._update_preview()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refine LaTeX: {str(e)}")
    
    def _clear_fields(self):
        """Clear input and output fields."""
        self.input_text.delete(1.0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self._update_preview()
    
    def _copy_latex(self):
        """Copy LaTeX output to clipboard."""
        latex_output = self.output_text.get(1.0, tk.END).strip()
        
        if not latex_output:
            messagebox.showinfo("Copy", "No LaTeX output to copy.")
            return
        
        if latex_output.startswith("Error:"):
            messagebox.showerror("Copy", "Cannot copy error message.")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(latex_output)
        
        # Show a subtle "Copied" message with auto-fade effect
        copy_label = ttk.Label(self.output_frame, 
                             text="Copied!", 
                             foreground=ModernTheme.SUCCESS,
                             font=("Segoe UI", 9, "italic"))
        copy_label.pack(anchor=tk.E, padx=5)
        
        # Schedule the label to be removed after 2 seconds
        self.root.after(2000, copy_label.destroy)
    
    def _update_preview(self):
        """Update the LaTeX preview with the current output."""
        # Clear previous content
        for widget in self.preview_container.winfo_children():
            widget.destroy()
        
        # Get current LaTeX content
        latex_content = self.output_text.get(1.0, tk.END).strip()
        
        if not latex_content:
            # Show empty state with explicitly set background color
            empty_frame = tk.Frame(self.preview_container, background=ModernTheme.CARD_BG)
            empty_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Fixed rely instead of duplicate relx
            
            empty_label = tk.Label(empty_frame,
                                text="Enter a Mathcad expression to see preview",
                                foreground=ModernTheme.TEXT_LIGHT,
                                background=ModernTheme.CARD_BG,
                                font=("Segoe UI", 11))
            empty_label.pack()
            return
        
        if latex_content.startswith("Error:"):
            # Show error state with explicit background color
            error_frame = tk.Frame(self.preview_container, background=ModernTheme.CARD_BG)
            error_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Fixed rely instead of duplicate relx
            
            error_label = tk.Label(error_frame,
                                text=latex_content,
                                foreground=ModernTheme.ERROR,
                                background=ModernTheme.CARD_BG,
                                font=("Segoe UI", 11))
            error_label.pack()
            return
        
        # Create a display for the LaTeX - prefer LaTeX over matplotlib
        if HAS_LATEX:
            self._render_with_latex(self.preview_container, latex_content)
        elif MATPLOTLIB_AVAILABLE:
            self._render_with_matplotlib(latex_content)
        else:
            self._render_text_preview(latex_content)
    
    def _render_with_matplotlib(self, latex_content):
        """Render LaTeX using Matplotlib if available."""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            
            # Create a frame with explicit background color
            matplotlib_frame = tk.Frame(self.preview_container, background=ModernTheme.CARD_BG)
            matplotlib_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Create figure with transparent background
            fig = plt.figure(figsize=(5, 3), dpi=100)
            fig.patch.set_facecolor('none')
            
            # Display the LaTeX expression
            plt.text(0.5, 0.5, f"${latex_content}$", 
                    fontsize=14, ha='center', va='center')
            
            # Hide axes
            plt.axis('off')
            
            # Create canvas
            canvas = FigureCanvasTkAgg(fig, master=matplotlib_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            # Fall back to text preview if rendering fails
            error_msg = f"Failed to render with Matplotlib: {str(e)}"
            self._render_text_preview(latex_content, error=error_msg)
    
    def _render_text_preview(self, latex_content, error=None, use_latex=False):
        """Render a text-based preview of the LaTeX."""
        # Create a frame with explicit background color
        preview_frame = tk.Frame(self.preview_container, background=ModernTheme.CARD_BG)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        if error:
            # Show error message with explicit background color
            error_label = tk.Label(preview_frame,
                                text=error,
                                foreground=ModernTheme.ERROR,
                                background=ModernTheme.CARD_BG,
                                font=("Segoe UI", 10),
                                wraplength=300)
            error_label.pack(pady=10)
        
        # Add rendered example if LaTeX is installed
        if use_latex:
            try:
                self._render_with_latex(preview_frame, latex_content)
            except Exception as e:
                error_label = tk.Label(preview_frame,
                                    text=f"LaTeX rendering failed: {str(e)}",
                                    foreground=ModernTheme.ERROR,
                                    background=ModernTheme.CARD_BG,
                                    font=("Segoe UI", 10))
                error_label.pack(pady=10)
        else:
            # Only show text preview if LaTeX rendering is not available
            # Create a Text widget with special formatting to highlight LaTeX syntax
            preview_text = tk.Text(preview_frame,
                                height=8,
                                width=40,
                                font=("Consolas", 12),
                                bg=ModernTheme.BG_DARK,
                                fg=ModernTheme.TEXT,
                                padx=15,
                                pady=15,
                                wrap=tk.WORD,
                                relief=tk.FLAT)
            preview_text.pack(fill=tk.BOTH, expand=True, pady=5)
            preview_text.insert(tk.END, latex_content)
            preview_text.config(state=tk.DISABLED)
    
    def _render_with_latex(self, parent_frame, latex_content):
        """Render using LaTeX if installed."""
        try:
            # Create a temporary directory for LaTeX files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create a minimal LaTeX document with additional padding and adjustments
                # Use the varwidth package to properly handle the width and prevent cutoffs
                latex_doc = f"""\\documentclass{{standalone}}
\\usepackage{{amsmath,amssymb}}
\\usepackage{{varwidth}}
\\usepackage[active,tightpage,displaymath,textmath]{{preview}}
\\setlength\\PreviewBorder{{5pt}}
\\begin{{document}}
\\begin{{varwidth}}{{\\linewidth}}
$${latex_content}$$
\\end{{varwidth}}
\\end{{document}}
"""
                
                # Write LaTeX document to temporary file
                tex_file = os.path.join(temp_dir, "preview.tex")
                with open(tex_file, "w", encoding="utf-8") as f:
                    f.write(latex_doc)
                
                # Compile LaTeX document to PDF
                process = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "-output-directory", temp_dir, tex_file],
                    capture_output=True,
                    text=True
                )
                
                if process.returncode != 0:
                    # Show compilation error
                    error_frame = tk.Frame(parent_frame, bg=ModernTheme.BG_COLOR)
                    error_frame.pack(fill=tk.BOTH, expand=True, pady=10)
                    
                    error_label = ttk.Label(
                        error_frame,
                        text="LaTeX compilation error:",
                        font=("Segoe UI", 10, "bold"),
                        foreground=ModernTheme.ERROR
                    )
                    error_label.pack(anchor=tk.W)
                    
                    # Get the specific error message from the LaTeX output
                    error_lines = [line for line in process.stdout.split('\n') 
                                  if line.startswith('!') or 'Error:' in line]
                    error_message = '\n'.join(error_lines[:3]) if error_lines else "Unknown error"
                    
                    error_text = tk.Text(
                        error_frame,
                        height=4,
                        width=40,
                        font=("Consolas", 9),
                        bg=ModernTheme.BG_DARK,
                        fg=ModernTheme.ERROR,
                        wrap=tk.WORD
                    )
                    error_text.pack(fill=tk.X, pady=5)
                    error_text.insert(tk.END, error_message)
                    error_text.config(state=tk.DISABLED)
                    return
                
                # If available, convert PDF to image for display
                if platform.system() == "Windows":
                    try:
                        from PIL import Image, ImageTk
                        import pdf2image
                        
                        # Convert PDF to image with higher DPI for better quality
                        pdf_file = os.path.join(temp_dir, "preview.pdf")
                        images = pdf2image.convert_from_path(pdf_file, dpi=1000)  # Increased DPI for higher quality
                        
                        if images:
                            # Create a container to display the image that fills the entire preview area
                            img_frame = ttk.Frame(parent_frame)
                            img_frame.pack(fill=tk.BOTH, expand=True)
                            
                            # Get the initial container size
                            parent_frame.update_idletasks()  # Update to get correct dimensions
                            frame_width = parent_frame.winfo_width()
                            frame_height = parent_frame.winfo_height()
                            
                            # Create a canvas to hold the image and allow for proper sizing
                            canvas = tk.Canvas(img_frame, 
                                              background=ModernTheme.CARD_BG,
                                              highlightthickness=0,
                                              bd=0)
                            canvas.pack(fill=tk.BOTH, expand=True)
                            
                            # Process the image
                            pil_image = images[0]
                            img_width, img_height = pil_image.size
                            
                            # Calculate the appropriate scale to fit the frame while maintaining aspect ratio
                            # Use 85% of available space to avoid edge cutoff
                            width_ratio = frame_width / img_width * 0.85
                            height_ratio = frame_height / img_height * 0.85
                            scale_factor = min(width_ratio, height_ratio)
                            
                            # Calculate new dimensions
                            new_width = int(img_width * scale_factor)
                            new_height = int(img_height * scale_factor)
                            
                            # Resize the image using LANCZOS for better quality
                            if scale_factor != 1:
                                pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
                            
                            # Save original image for zooming
                            self.original_image = pil_image
                            self.current_scale = 1.0
                            
                            # Convert to PhotoImage
                            img_tk = ImageTk.PhotoImage(pil_image)
                            
                            # Create image on canvas, centered
                            img_id = canvas.create_image(frame_width//2, frame_height//2, anchor=tk.CENTER, image=img_tk)
                            canvas.image = img_tk  # Keep a reference to prevent garbage collection
                            
                            # Variables for panning
                            self._drag_data = {"x": 0, "y": 0, "item": img_id}
                            
                            # Bind mouse events for zooming and panning
                            canvas.bind("<ButtonPress-1>", lambda event, canvas=canvas: self._start_drag(event, canvas))
                            canvas.bind("<B1-Motion>", lambda event, canvas=canvas: self._drag(event, canvas))
                            canvas.bind("<MouseWheel>", lambda event, canvas=canvas, pil_image=pil_image: self._zoom(event, canvas, pil_image))
                            # For Linux/Mac systems which use different mouse wheel events
                            canvas.bind("<Button-4>", lambda event, canvas=canvas, pil_image=pil_image: self._zoom_linux(event, canvas, pil_image, 1))
                            canvas.bind("<Button-5>", lambda event, canvas=canvas, pil_image=pil_image: self._zoom_linux(event, canvas, pil_image, -1))
                            
                            # Add resize handler to keep image centered and appropriately sized
                            def on_resize(event):
                                # Update canvas dimensions
                                w, h = event.width, event.height
                                canvas.delete("all")  # Clear the canvas
                                
                                # Calculate new dimensions for the image
                                width_ratio = w / img_width * 0.85
                                height_ratio = h / img_height * 0.85
                                scale = min(width_ratio, height_ratio)
                                
                                new_w = int(img_width * scale * self.current_scale)
                                new_h = int(img_height * scale * self.current_scale)
                                
                                # Resize the image with high quality resampling
                                resized_img = self.original_image.resize((new_w, new_h), Image.LANCZOS)
                                new_img_tk = ImageTk.PhotoImage(resized_img)
                                
                                # Place the new image
                                img_id = canvas.create_image(w//2, h//2, anchor=tk.CENTER, image=new_img_tk)
                                canvas.image = new_img_tk  # Keep a reference
                                self._drag_data["item"] = img_id
                            
                            # Bind the resize event
                            canvas.bind("<Configure>", on_resize)
                            
                            # Add zoom control buttons
                            control_frame = tk.Frame(img_frame, bg=ModernTheme.CARD_BG)
                            control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
                            
                            zoom_in_btn = ttk.Button(control_frame, text="Zoom In", 
                                                  command=lambda: self._zoom_button(canvas, pil_image, 1.1))
                            zoom_in_btn.pack(side=tk.LEFT, padx=5)
                            
                            zoom_out_btn = ttk.Button(control_frame, text="Zoom Out", 
                                                   command=lambda: self._zoom_button(canvas, pil_image, 0.9))
                            zoom_out_btn.pack(side=tk.LEFT, padx=5)
                            
                            reset_btn = ttk.Button(control_frame, text="Reset View", 
                                                   command=lambda: self._reset_view(canvas, self.original_image))
                            reset_btn.pack(side=tk.LEFT, padx=5)
                            
                            # Add instructions label
                            instruction_label = ttk.Label(
                                control_frame,
                                text="Drag to pan • Mouse wheel to zoom",
                                font=("Segoe UI", 8),
                                foreground=ModernTheme.TEXT_LIGHT
                            )
                            instruction_label.pack(side=tk.RIGHT, padx=10)
                            
                            return
                    except (ImportError, Exception) as e:
                        # Fall through to the message below if we can't render the image
                        pass
                
                # If we couldn't render the image (e.g., missing dependencies),
                # show a message about successful compilation
                success_label = ttk.Label(
                    parent_frame,
                    text="LaTeX compiled successfully! Install PIL and pdf2image to view the rendered output.",
                    font=("Segoe UI", 11),
                    foreground=ModernTheme.SUCCESS,
                    wraplength=350
                )
                success_label.pack(pady=10)
                
        except Exception as e:
            # Show error message
            error_label = ttk.Label(
                parent_frame,
                text=f"Error rendering LaTeX: {str(e)}",
                font=("Segoe UI", 10),
                foreground=ModernTheme.ERROR,
                wraplength=350
            )
            error_label.pack(pady=10)
            
    def _start_drag(self, event, canvas):
        """Start panning the image."""
        # Record the initial coordinates when drag begins
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        
    def _drag(self, event, canvas):
        """Pan the image as the mouse moves."""
        # Calculate the distance moved
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        
        # Move the image
        canvas.move(self._drag_data["item"], dx, dy)
        
        # Record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
    
    def _zoom(self, event, canvas, original_image):
        """Zoom in/out with the mouse wheel (Windows)."""
        # Get scale factor based on wheel direction
        if event.delta > 0:
            scale_factor = 1.1  # Zoom in
        else:
            scale_factor = 0.9  # Zoom out
            
        self._apply_zoom(canvas, original_image, scale_factor, event.x, event.y)
    
    def _zoom_linux(self, event, canvas, original_image, direction):
        """Zoom in/out with the mouse wheel (Linux/Mac)."""
        scale_factor = 1.1 if direction > 0 else 0.9
        self._apply_zoom(canvas, original_image, scale_factor, event.x, event.y)
    
    def _zoom_button(self, canvas, original_image, scale_factor):
        """Zoom in/out using buttons."""
        # Calculate the center of the canvas for zoom origin
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        self._apply_zoom(canvas, original_image, scale_factor, canvas_width//2, canvas_height//2)
    
    def _apply_zoom(self, canvas, original_image, scale_factor, x, y):
        """Apply zoom at a specific point with a scale factor."""
        # Update current scale
        self.current_scale *= scale_factor
        
        # Limit zoom level to reasonable bounds
        if self.current_scale < 0.2:
            self.current_scale = 0.2
        elif self.current_scale > 5.0:
            self.current_scale = 5.0
        
        # Get the original image size
        img_width, img_height = original_image.size
        
        # Calculate new dimensions
        new_width = int(img_width * self.current_scale)
        new_height = int(img_height * self.current_scale)
        
        # Resize with high quality
        resized_img = self.original_image.resize((new_width, new_height), Image.LANCZOS)
        new_img_tk = ImageTk.PhotoImage(resized_img)
        
        # Get current position of the image
        img_id = self._drag_data["item"]
        current_coords = canvas.coords(img_id)
        
        if current_coords:
            # Calculate zoom point relative to image
            current_x, current_y = current_coords
            rel_x = (x - current_x) / (new_width / scale_factor)
            rel_y = (y - current_y) / (new_height / scale_factor)
            
            # Calculate new position after zoom
            new_x = x - rel_x * scale_factor
            new_y = y - rel_y * scale_factor
            
            # Remove old image and create new one
            canvas.delete(img_id)
            new_img_id = canvas.create_image(new_x, new_y, image=new_img_tk)
            
            # Update references
            canvas.image = new_img_tk
            self._drag_data["item"] = new_img_id
        else:
            # If no current coordinates, just center the image
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
            # Remove old image and create new one
            canvas.delete(img_id)
            new_img_id = canvas.create_image(canvas_width//2, canvas_height//2, 
                                           anchor=tk.CENTER, image=new_img_tk)
            
            # Update references
            canvas.image = new_img_tk
            self._drag_data["item"] = new_img_id
    
    def _reset_view(self, canvas, original_image):
        """Reset the view to original position and scale."""
        # Reset scale to 1.0
        self.current_scale = 1.0
        
        # Get the original image size
        img_width, img_height = original_image.size
        
        # Get canvas dimensions
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        # Calculate the appropriate scale to fit the canvas while maintaining aspect ratio
        # Use 85% of available space to avoid edge cutoff
        width_ratio = canvas_width / img_width * 0.85
        height_ratio = canvas_height / img_height * 0.85
        scale_factor = min(width_ratio, height_ratio)
        
        # Calculate new dimensions
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)
        
        # Resize the image using LANCZOS for better quality
        resized_img = self.original_image.resize((new_width, new_height), Image.LANCZOS)
        new_img_tk = ImageTk.PhotoImage(resized_img)
        
        # Remove old image and create new one at center
        canvas.delete(self._drag_data["item"])
        new_img_id = canvas.create_image(canvas_width//2, canvas_height//2, 
                                       anchor=tk.CENTER, image=new_img_tk)
        
        # Update references
        canvas.image = new_img_tk
        self._drag_data["item"] = new_img_id

    def _clear_text(self):
        """Clear the input and output fields."""
        self.input_text.delete(1.0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self._update_preview()
    
    def _clear_placeholder(self, event):
        """Clear placeholder text when input field is focused."""
        if self.input_text.tag_ranges("placeholder"):
            self.input_text.delete(1.0, tk.END)
            self.input_text.tag_remove("placeholder", "1.0", "end")
    
    def _load_example(self):
        """Load an example Mathcad expression into the input field."""
        examples = [
            # Basic Examples
            "(x + y)",
            "(α + β)",
            "(/ x y)",
            "(^ x 2)",
            
            # Advanced Examples
            "(@INTEGRAL 0 1 x^2 x)",
            "(@DERIV x 1 (^ x 2))",
            "(@PART_DERIV x 1 (@PARENS (+ x y)))",
            "(@LIMIT x 0 (@PARENS (/ (^ x 2) x)))",
            "(@PRODUCT (@IS i 1) n i)",
            "(@NTHROOT 2 x)",
            "(@NTHROOT 3 x)",
            "(@APPLY sin (@ARGS x))",
            "(@APPLY ln (@ARGS x))",
            "(@APPLY abs (@ARGS x))",
            "(+ (* 2 x) (/ y z))",
            "(@IS (^ x 2) (+ y z))",
            "(@LEQ x y)",
            "(@GEQ x y)",
            "(@INTEGRAL 0 1 (@INTEGRAL 0 y x^2 x) y)"
        ]
        
        import random
        example = random.choice(examples)
        
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(tk.END, example)
        self.input_text.tag_remove("placeholder", "1.0", "end")
        
        # Automatically convert the example
        self._convert_expression()
    
    def _on_key_release(self, event):
        """Handle key release events to update preview in real-time."""
        # Only update preview on real key presses, not on special keys
        if event.keysym not in ('Shift_L', 'Shift_R', 'Control_L', 'Control_R', 
                               'Alt_L', 'Alt_R', 'Caps_Lock', 'Tab'):
            # Add a small delay to avoid too frequent updates
            if not hasattr(self, '_convert_after_id'):
                self._convert_after_id = None
            
            # Cancel previous delayed conversion if exists
            if self._convert_after_id:
                self.root.after_cancel(self._convert_after_id)
            
            # Schedule new conversion with delay
            self._convert_after_id = self.root.after(300, self._convert_expression)

    def _on_sash_moved(self, event):
        """Track when user manually adjusts sash positions."""
        self.user_adjusted_sashes = True

    def _on_output_modified(self, event):
        """Handle output text modifications and resize the output pane if user hasn't manually adjusted sashes."""
        # Reset the modified flag
        self.output_text.edit_modified(False)
        
        # Update the preview with the new content
        self._update_preview()
        
        # Automatically resize the output pane based on content if user hasn't manually adjusted
        if not self.user_adjusted_sashes:
            # Get current content and count lines
            content = self.output_text.get(1.0, tk.END)
            line_count = content.count('\n') + 1
            
            # Calculate new height (limit to reasonable size)
            min_height = 3  # Minimum number of visible lines
            max_height = 12  # Maximum number of visible lines
            new_line_count = max(min_height, min(line_count, max_height))
            
            # Calculate approximately how many pixels per line
            font = self.output_text.cget("font")
            if isinstance(font, str):
                font_parts = font.split()
                font_size = int(font_parts[-1]) if len(font_parts) > 1 else 11
            else:
                font_size = 11
            
            # Approximate height per line (font size + padding)
            line_height = font_size + 4
            
            # Get the total height of the paned window
            total_height = self.vertical_paned_window.winfo_height()
            
            # Calculate new sash positions
            first_sash = total_height // 5  # Keep input at ~20%
            second_sash = first_sash + (new_line_count * line_height) + 50  # Add space for header/buttons
            
            # Adjust second sash position, but don't let it exceed 70% of the window
            max_second_sash = int(total_height * 0.7)
            second_sash = min(second_sash, max_second_sash)
            
            # Update sash positions
            self.vertical_paned_window.sashpos(0, first_sash)
            self.vertical_paned_window.sashpos(1, second_sash)

def main():
    """Main function to run the application."""
    root = tk.Tk()
    app = MathcadToLatexGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()