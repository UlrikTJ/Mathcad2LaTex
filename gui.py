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
import io  # Add io module for BytesIO
import warnings  # Import warnings module
from tkinter import ttk, filedialog, messagebox, scrolledtext
from mathcad_to_latex import MathcadToLatexTranslator

# Import PIL modules at module level
try:
    from PIL import Image, ImageTk
    # Disable DecompressionBombWarning
    Image.MAX_IMAGE_PIXELS = None  # Remove the pixel limit restriction
    warnings.filterwarnings("ignore", category=Image.DecompressionBombWarning)
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
        self.render_format = tk.StringVar(value="pdf")
        self.first_render = False  # Track first render
        
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
        
        # Add copy button next to convert button
        self.copy_button = ttk.Button(
            self.controls_frame, 
            text="Copy LaTeX", 
            command=self._copy_latex,
            style="Secondary.TButton"
        )
        self.copy_button.pack(side=tk.RIGHT, padx=(5, 0))
        
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
    
    def _setup_preview_section(self):
        """Set up the preview section with a LaTeX preview."""
        # Create main preview frame with a better structure
        self.preview_main_frame = ttk.Frame(self.preview_frame)
        self.preview_main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        
        # Create header with rendering option controls
        preview_header_frame = ttk.Frame(self.preview_main_frame)
        preview_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.preview_header = ttk.Label(preview_header_frame, 
                                      text="LaTeX Preview",
                                      style="Subheader.TLabel")
        self.preview_header.pack(side=tk.LEFT)
        
        # Create a separate frame for toolbar
        self.toolbar_frame = ttk.Frame(self.preview_main_frame)
        self.toolbar_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Add zoom controls to the toolbar
        zoom_out_btn = ttk.Button(self.toolbar_frame, 
                                text="➖",
                                width=3,
                                command=self._zoom_out)
        zoom_out_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.zoom_level = ttk.Label(self.toolbar_frame,
                                  text="100%",
                                  width=8)
        self.zoom_level.pack(side=tk.LEFT, padx=5)
        
        zoom_in_btn = ttk.Button(self.toolbar_frame, 
                               text="➕",
                               width=3,
                               command=self._zoom_in)
        zoom_in_btn.pack(side=tk.LEFT, padx=5)
        
        reset_zoom_btn = ttk.Button(self.toolbar_frame,
                                  text="Reset to 100%",
                                  command=self._reset_zoom)
        reset_zoom_btn.pack(side=tk.LEFT, padx=5)
        
        # Add fit-to-view button with a distinctive icon
        fit_view_btn = ttk.Button(self.toolbar_frame,
                                text="🔍 Fit to View",
                                command=self._fit_to_view)
        fit_view_btn.pack(side=tk.LEFT, padx=15)
        
        save_btn = ttk.Button(self.toolbar_frame,
                            text="Save as Image",
                            command=self._save_preview)
        save_btn.pack(side=tk.RIGHT)
        
        # Create a container with specific background color - separate from toolbar
        self.preview_container = tk.Frame(self.preview_main_frame, 
                                        background=ModernTheme.CARD_BG,
                                        highlightthickness=1,
                                        highlightbackground=ModernTheme.BG_DARK)
        self.preview_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Bind keyboard shortcuts for zooming
        self.root.bind("<Control-equal>", lambda e: self._zoom_in())
        self.root.bind("<Control-plus>", lambda e: self._zoom_in())
        self.root.bind("<Control-minus>", lambda e: self._zoom_out())
        self.root.bind("<Control-0>", lambda e: self._fit_to_view())
    
    def _zoom_in(self):
        """Increase the zoom level."""
        self.current_scale = min(5.0, self.current_scale * 1.25)
        self.zoom_level.config(text=f"{int(self.current_scale * 100)}%")
        self._apply_zoom()  # Apply zoom to existing image instead of re-rendering
    
    def _zoom_out(self):
        """Decrease the zoom level."""
        self.current_scale = max(0.25, self.current_scale / 1.25)
        self.zoom_level.config(text=f"{int(self.current_scale * 100)}%")
        self._apply_zoom()  # Apply zoom to existing image instead of re-rendering
    
    def _reset_zoom(self):
        """Reset zoom level to 100%."""
        if hasattr(self, 'original_image') and self.original_image is not None:
            self.current_scale = 1.0
            self.zoom_level.config(text="100%")
            self._apply_zoom()
    
    def _fit_to_view(self):
        """Adjust zoom to fit the equation to the preview container."""
        if not hasattr(self, 'original_image') or self.original_image is None:
            return
            
        # Get the preview container dimensions
        container_width = self.preview_container.winfo_width() - 20  # Subtract padding
        container_height = self.preview_container.winfo_height() - 20
        
        if container_width <= 0 or container_height <= 0:
            # If container is not properly sized yet, use default dimensions
            container_width = 600
            container_height = 300
        
        # Make a copy of the original image for cropping
        cropped_image = self.original_image.copy()
        
        # Auto-crop the image to focus on just the equation content
        cropped_image = self._autocrop_image(cropped_image)
        
        if cropped_image.width == 0 or cropped_image.height == 0:
            # Handle edge case of empty image
            return
            
        # Calculate scale factors to fit width and height
        width_scale = container_width / cropped_image.width
        height_scale = container_height / cropped_image.height
        
        # Use the smaller scale to ensure entire equation fits
        fit_scale = min(width_scale, height_scale) * 0.9  # Add a small margin
        
        # Set reasonable bounds for the scale
        fit_scale = max(0.25, min(fit_scale, 5.0))
        
        # Update the scale and zoom label
        self.current_scale = fit_scale
        self.zoom_level.config(text=f"{int(self.current_scale * 100)}%")
        
        # Store the cropped image as the new original for display
        self.original_image = cropped_image
        
        # Apply the zoom to the newly cropped image
        self._apply_zoom()
    
    def _apply_zoom(self):
        """Apply zoom to the existing image without re-rendering LaTeX."""
        if not hasattr(self, 'original_image') or self.original_image is None:
            # If there's no original image, we need to render it first
            self._update_preview()
            return
            
        # Clear only the preview container without affecting the toolbar
        for widget in self.preview_container.winfo_children():
            widget.destroy()
            
        # Resize the original image using the current scale
        new_width = int(self.original_image.width * self.current_scale)
        new_height = int(self.original_image.height * self.current_scale)
        resized_image = self.original_image.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to PhotoImage for display
        photo_image = ImageTk.PhotoImage(resized_image)
        
        # Get the current container dimensions
        canvas_width = self.preview_container.winfo_width()
        canvas_height = self.preview_container.winfo_height()
        
        # Ensure we have valid dimensions
        if canvas_width <= 0:
            canvas_width = 800
        if canvas_height <= 0:
            canvas_height = 400
        
        # Create canvas with scrollbars
        canvas = tk.Canvas(self.preview_container, 
                          width=canvas_width, 
                          height=canvas_height,
                          borderwidth=0, 
                          highlightthickness=0, 
                          bg=ModernTheme.CARD_BG)
        
        # Add scrollbars if needed
        h_scrollbar = ttk.Scrollbar(self.preview_container, orient=tk.HORIZONTAL, command=canvas.xview)
        v_scrollbar = ttk.Scrollbar(self.preview_container, orient=tk.VERTICAL, command=canvas.yview)
        
        # Configure canvas scrolling
        canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Pack scrollbars only if needed
        if new_width > canvas_width:
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        if new_height > canvas_height:
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create image on canvas
        canvas_image = canvas.create_image(0, 0, anchor=tk.NW, image=photo_image)
        canvas.photo = photo_image  # Keep reference to prevent garbage collection
        
        # Configure canvas scroll region
        canvas.configure(scrollregion=(0, 0, new_width, new_height))
        
        # Center the image in the visible area
        if new_width < canvas_width:
            canvas.xview_moveto((new_width - canvas_width) / (2 * new_width) if new_width > 0 else 0)
        else:
            canvas.xview_moveto(0)
        if new_height < canvas_height:
            canvas.yview_moveto((new_height - canvas_height) / (2 * new_height) if new_height > 0 else 0)
        else:
            canvas.yview_moveto(0)
        
        # Enable dragging the image with the mouse
        canvas.bind("<ButtonPress-1>", self._scroll_start)
        canvas.bind("<B1-Motion>", self._scroll_move)
        canvas.bind("<MouseWheel>", self._on_mousewheel)  # For Windows and MacOS
        canvas.bind("<Button-4>", self._on_mousewheel)    # For Linux scroll up
        canvas.bind("<Button-5>", self._on_mousewheel)    # For Linux scroll down

    def _convert_expression(self):
        """Convert Mathcad expression to LaTeX."""
        mathcad_expr = self.input_text.get(1.0, tk.END).strip()
        
        if not mathcad_expr:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "")
            self._update_preview()
            return
        
        try:
            # Create a translator instance and use its translate method
            translator = MathcadToLatexTranslator()
            latex_expr = translator.translate(mathcad_expr)
            
            # Update output field
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, latex_expr)
            
            # Update preview
            self._update_preview()
        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Error: {str(e)}")
            self._update_preview()
    
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

    def _render_error(self, container, error_message):
        """Render an error message in the preview container."""
        # Clear any existing content
        for widget in container.winfo_children():
            widget.destroy()
        
        # Create a frame with explicit background color
        error_frame = tk.Frame(container, background=ModernTheme.CARD_BG)
        error_frame.place(relx=0.5, relwidth=0.8, rely=0.5, anchor=tk.CENTER)
        
        # Create the error message with red text
        error_label = tk.Label(error_frame,
                            text=error_message,
                            foreground=ModernTheme.ERROR,
                            background=ModernTheme.CARD_BG,
                            font=("Segoe UI", 11),
                            wraplength=container.winfo_width() - 40)  # Allow wrapping with margin
        error_label.pack(padx=10, pady=10)

    def _create_latex_document(self, latex_content):
        """
        Create a complete LaTeX document containing the given LaTeX expression.
        
        Args:
            latex_content (str): The LaTeX equation or expression to include
            
        Returns:
            str: Complete LaTeX document as a string
        """
        # Create a standard LaTeX document structure with appropriate packages
        # Using wider margins and landscape orientation for longer expressions
        document = r"""
\documentclass[12pt]{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{mathtools}
\usepackage{bm}
\usepackage[landscape,margin=0.1in]{geometry}
\pagestyle{empty}

\begin{document}
\begin{center}
\begin{equation*}
""" + latex_content + r"""
\end{equation*}
\end{center}
\end{document}
"""
        return document
        
    def _render_text_preview(self, latex_content):
        """Render a simple text preview of the LaTeX content when better rendering is not available."""
        # Clear any existing content
        for widget in self.preview_container.winfo_children():
            widget.destroy()
            
        # Create a frame with a light background
        preview_frame = tk.Frame(self.preview_container, background=ModernTheme.CARD_BG)
        preview_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Create an informative message
        message_label = tk.Label(preview_frame,
                                text="LaTeX Preview (Text Only):",
                                foreground=ModernTheme.PRIMARY,
                                background=ModernTheme.CARD_BG,
                                font=("Segoe UI", 11, "bold"))
        message_label.pack(pady=(10, 5))
        
        # Create a text widget to display the LaTeX content
        text_preview = scrolledtext.ScrolledText(preview_frame,
                                              width=60,
                                              height=10,
                                              font=("Consolas", 12),
                                              bg=ModernTheme.BG_COLOR,
                                              fg=ModernTheme.TEXT,
                                              relief=tk.FLAT,
                                              padx=10,
                                              pady=10)
        text_preview.pack(padx=20, pady=10)
        
        # Insert the LaTeX content
        text_preview.insert(tk.END, latex_content)
        text_preview.config(state=tk.DISABLED)  # Make it read-only
        
        # Add a note about installation
        note_label = tk.Label(preview_frame,
                            text="Note: Install LaTeX or matplotlib for rendered previews",
                            foreground=ModernTheme.TEXT_LIGHT,
                            background=ModernTheme.CARD_BG,
                            font=("Segoe UI", 9, "italic"))
        note_label.pack(pady=(0, 10))
    
    def _update_preview(self):
        """Update the LaTeX preview with the current output."""
        # Clear any existing content
        for widget in self.preview_container.winfo_children():
            widget.destroy()
            
        # Get the LaTeX content from the output text
        latex_content = self.output_text.get(1.0, tk.END).strip()
        
        if not latex_content:
            # If there's no content, show an empty placeholder
            self._render_error(self.preview_container, "No LaTeX to preview. Enter a Mathcad expression and convert it.")
            return
        
        if latex_content.startswith("Error:"):
            # Show error message
            self._render_error(self.preview_container, latex_content)
            return
        
        # Check if we should use PDF rendering
        use_svg = False
        
        # Try to render the LaTeX using different methods
        self._render_latex_preview(latex_content, use_svg)
            
    def _render_latex_preview(self, latex_content, use_svg=False):
        """Render LaTeX preview using the best available method."""
        try:
            # First try to use LaTeX if it's installed (best quality)
            if HAS_LATEX:
                self._render_with_latex(latex_content, use_svg)
            # If LaTeX isn't available, try matplotlib (decent quality)
            elif MATPLOTLIB_AVAILABLE:
                self._render_with_matplotlib(latex_content)
            # If nothing else is available, just show text preview
            else:
                self._render_text_preview(latex_content)
        except Exception as e:
            # If rendering fails, show error
            self._render_error(self.preview_container, f"Error rendering preview: {str(e)}")
            
    def _render_with_latex(self, latex_content, use_svg=False):
        """Render LaTeX using native LaTeX compiler."""
        # Create a temporary directory to work in
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create paths for the files
            tex_file = os.path.join(temp_dir, "preview.tex")
            
            # Create the full LaTeX document
            document = self._create_latex_document(latex_content)
            
            # Write the LaTeX document to a temporary file
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(document)
            
            # Determine output format based on user selection
            output_format = "pdf"
                
            # Run LaTeX command to generate output
            try:
                if output_format == "pdf":
                    # Run pdflatex to generate PDF
                    process = subprocess.run(
                        ["pdflatex", "-interaction=nonstopmode", "-output-directory", temp_dir, tex_file],
                        capture_output=True,
                        timeout=5
                    )
                    
                    # Check if the compilation was successful
                    if process.returncode != 0:
                        error_msg = process.stderr.decode('utf-8', errors='replace')
                        # Show just the most relevant part of the error
                        if "!" in error_msg:
                            error_msg = error_msg[error_msg.find("!"):]
                            error_msg = error_msg[:error_msg.find("\n\n")]
                        raise Exception(f"LaTeX compilation failed: {error_msg}")
                    
                    # Convert PDF to image using PIL
                    pdf_file = os.path.join(temp_dir, "preview.pdf")
                    self._render_pdf_preview(pdf_file)
            
            except subprocess.TimeoutExpired:
                raise Exception("LaTeX compilation timed out. The expression might be too complex.")
                
    def _render_pdf_preview(self, pdf_file):
        """Render a PDF file as an image in the preview container."""
        try:
            # Try to convert PDF to image using Pillow with pdf2image
            from pdf2image import convert_from_path
            
            # Convert first page of PDF to image
            images = convert_from_path(pdf_file, dpi=600, first_page=1, last_page=1)
            if not images:
                raise Exception("Failed to convert PDF to image")
                
            # Save the original image for zooming
            self.original_image = self._autocrop_image(images[0])
            
            # Apply the current zoom level to the image
            self._apply_zoom()
                
        except ImportError:
            # If pdf2image or poppler is not installed
            self._render_error(self.preview_container, 
                            "PDF to image conversion requires pdf2image package.\n"
                            "Install it with: pip install pdf2image\n"
                            "And ensure poppler is installed on your system.")
            
    def _render_with_matplotlib(self, latex_content):
        """Render LaTeX using matplotlib's math rendering."""
        try:
            import matplotlib.pyplot as plt
            from matplotlib import rcParams
            import io
            
            # Configure matplotlib for LaTeX rendering
            rcParams['text.usetex'] = True
            rcParams['font.family'] = 'serif'
            rcParams['font.serif'] = ['Computer Modern Roman']
            rcParams['text.latex.preamble'] = r'\usepackage{amsmath} \usepackage{amssymb} \usepackage{amsfonts}'
            
            # Create a figure with appropriate size
            fig = plt.figure(figsize=(12, 8), dpi=100)
            
            # No axes, just the equation
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_axis_off()
            
            # Place the equation in the center
            ax.text(0.5, 0.5, f"${latex_content}$", 
                  fontsize=18, ha='center', va='center')
            
            # Render to a PIL Image
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, 
                      bbox_inches='tight', pad_inches=0.1)
            plt.close(fig)
            
            # Open the image from the buffer
            buf.seek(0)
            image = Image.open(buf)
            
            # Save the original image for zooming
            self.original_image = self._autocrop_image(image)
            
            # Apply the current zoom level to the image
            self._apply_zoom()
            
        except Exception as e:
            # If matplotlib rendering fails
            self._render_error(self.preview_container, 
                            f"Matplotlib rendering failed: {str(e)}\n"
                            f"Try installing LaTeX for better rendering.")
            
    def _save_preview(self):
        """Save the current preview image to a file."""
        if not hasattr(self, 'original_image') or self.original_image is None:
            messagebox.showinfo("Save Preview", "Nothing to save. Generate a preview first.")
            return
            
        # Ask for file location
        file_types = [
            ("PNG Image", "*.png"),
            ("JPEG Image", "*.jpg"),
            ("All Files", "*.*")
        ]
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=file_types,
            title="Save Preview As"
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            # Save the image
            self.original_image.save(file_path)
            messagebox.showinfo("Save Preview", f"Preview saved successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preview: {str(e)}")
            
    def _scroll_start(self, event):
        """Start scrolling/dragging the image."""
        self._drag_data["item"] = event.widget
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        
    def _scroll_move(self, event):
        """Handle mouse dragging to scroll the canvas."""
        if not self._drag_data["item"]:
            return
            
        # Calculate the distance moved
        dx = self._drag_data["x"] - event.x
        dy = self._drag_data["y"] - event.y
        
        # Update canvas scroll position
        canvas = self._drag_data["item"]
        canvas.xview_scroll(dx, "units")
        canvas.yview_scroll(dy, "units")
        
        # Update the drag start position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        
    def _on_mousewheel(self, event):
        """Handle mousewheel events for scrolling."""
        canvas = event.widget
        
        # Determine scroll direction and amount based on platform
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
            # Scroll up
            canvas.yview_scroll(-1, "units")
        elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            # Scroll down
            canvas.yview_scroll(1, "units")
    
    def _autocrop_image(self, image, padding=10):
        """
        Automatically crop an image to its content with optional padding.
        
        Args:
            image: PIL image to crop
            padding: Padding to add around the content in pixels
            
        Returns:
            PIL Image: Cropped image, or original if no content found
        """
        # Convert to grayscale for content detection
        grayscale = image.convert('L')
        
        # Get content bounding box
        bbox = self._get_content_bbox(grayscale)
        
        if not bbox:
            return image  # No content found, return original
        
        # Unpack bounding box
        left, top, right, bottom = bbox
        
        # Add padding
        left = max(0, left - padding)
        top = max(0, top - padding)
        right = min(image.width, right + padding)
        bottom = min(image.height, bottom + padding)
        
        # Crop to content
        return image.crop((left, top, right, bottom))
    
    def _get_content_bbox(self, grayscale_image, threshold=245):
        """
        Find the bounding box of content in a grayscale image.
        
        Args:
            grayscale_image: Grayscale PIL image
            threshold: Pixel value threshold (0-255) to determine content vs background
            
        Returns:
            tuple: (left, top, right, bottom) or None if no content found
        """
        width, height = grayscale_image.size
        pixels = grayscale_image.load()
        
        # Find content boundaries
        left, top, right, bottom = width, height, 0, 0
        found_content = False
        
        # Scan for content
        for y in range(height):
            for x in range(width):
                # If pixel is darker than threshold, it's content
                if pixels[x, y] < threshold:
                    found_content = True
                    left = min(left, x)
                    top = min(top, y)
                    right = max(right, x)
                    bottom = max(bottom, y)
        
        if found_content:
            return (left, top, right, bottom)
        return None

def main():
    """Main function to run the application."""
    root = tk.Tk()
    app = MathcadToLatexGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
