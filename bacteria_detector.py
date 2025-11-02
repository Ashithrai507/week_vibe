import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                           QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, 
                           QFrame, QGroupBox, QTextEdit, QMenuBar, QMenu, QAction,
                           QStatusBar, QMainWindow, QSlider, QScrollArea)
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QTimer
from ultralytics import YOLO

class Windows95GroupBox(QGroupBox):
    """Classic Windows 95 style group box"""
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("""
            QGroupBox {
                background-color: #c0c0c0;
                border: 2px solid;
                border-color: #ffffff #808080 #808080 #ffffff;
                margin-top: 10px;
                padding-top: 10px;
                font-family: 'MS Sans Serif', sans-serif;
                font-size: 11px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #000000;
            }
        """)

class BacteriaDetector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bacteria Colony Detection - Multi-Model Application")
        self.setGeometry(100, 50, 1100, 800)
        
        # Classic Windows 95 color scheme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(192, 192, 192))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(192, 192, 192))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        self.setPalette(palette)
        
        # Windows 95 style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #c0c0c0;
            }
            QWidget {
                background-color: #c0c0c0;
                font-family: 'MS Sans Serif', 'Microsoft Sans Serif', sans-serif;
                font-size: 11px;
                color: #000000;
            }
            QPushButton {
                background-color: #c0c0c0;
                border: 2px solid;
                border-color: #ffffff #000000 #000000 #ffffff;
                padding: 5px 15px;
                font-family: 'MS Sans Serif', sans-serif;
                font-size: 11px;
                font-weight: bold;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #c0c0c0;
            }
            QPushButton:pressed {
                border-color: #000000 #ffffff #ffffff #000000;
                padding: 6px 14px 4px 16px;
            }
            QPushButton:disabled {
                color: #808080;
                border-color: #ffffff #808080 #808080 #ffffff;
            }
            QLabel {
                background-color: transparent;
                color: #000000;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 2px solid;
                border-color: #808080 #ffffff #ffffff #808080;
                font-family: 'Fixedsys', 'Courier New', monospace;
                font-size: 12px;
                color: #000000;
            }
            QSlider::groove:horizontal {
                border: 2px solid;
                border-color: #808080 #ffffff #ffffff #808080;
                height: 4px;
                background: #c0c0c0;
            }
            QSlider::handle:horizontal {
                background: #c0c0c0;
                border: 2px solid;
                border-color: #ffffff #000000 #000000 #ffffff;
                width: 15px;
                margin: -6px 0;
            }
            QScrollArea {
                border: 2px solid;
                border-color: #808080 #ffffff #ffffff #808080;
                background-color: #ffffff;
            }
            QMenuBar {
                background-color: #c0c0c0;
                border: none;
                font-family: 'MS Sans Serif', sans-serif;
                font-size: 11px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background-color: #000080;
                color: #ffffff;
            }
            QMenu {
                background-color: #c0c0c0;
                border: 2px solid;
                border-color: #ffffff #000000 #000000 #ffffff;
            }
            QMenu::item {
                padding: 4px 25px 4px 10px;
            }
            QMenu::item:selected {
                background-color: #000080;
                color: #ffffff;
            }
            QStatusBar {
                background-color: #c0c0c0;
                border-top: 2px solid;
                border-color: #ffffff #808080 #808080 #ffffff;
            }
            QStatusBar::item {
                border: 2px solid;
                border-color: #808080 #ffffff #ffffff #808080;
            }
        """)

        # Define available models
        self.model_definitions = {
            "Two Bacteria Model": "new_alcy.pt",
            "Model 2": "model2.pt",
            #"Model 3": "new_",
        }
        
        self.loaded_models = {}
        self.current_pixmap = None  # Store the current image
        self.zoom_level = 100  # Default zoom level 100%

        self.init_ui()
        self.load_all_models()

    def load_all_models(self):
        """Load all available models at startup"""
        self.statusbar.showMessage("Loading models...")
        self.status_label.setText("Status: Loading...")
        QApplication.processEvents()
        
        loaded_count = 0
        failed_models = []
        model_names = []
        
        for model_name, model_path in self.model_definitions.items():
            if os.path.exists(model_path):
                try:
                    model = YOLO(model_path)
                    self.loaded_models[model_name] = model
                    model_names.append(model_name)
                    loaded_count += 1
                    print(f"✓ Loaded: {model_name}")
                except Exception as e:
                    failed_models.append(f"{model_name}: {str(e)}")
                    print(f"✗ Failed to load {model_name}: {str(e)}")
            else:
                failed_models.append(f"{model_name}: File not found")
                print(f"✗ Model file not found: {model_path}")
        
        if loaded_count > 0:
            models_text = "Loaded: " + ", ".join(model_names)
            self.models_info_label.setText(models_text)
            self.statusbar.showMessage(f"Loaded {loaded_count} model(s) - Ready to detect")
            self.status_label.setText(f"Status: Ready ({loaded_count} models)")
            
            if failed_models:
                msg = f"Successfully loaded {loaded_count} model(s).\n\n"
                msg += "Failed models:\n" + "\n".join(failed_models)
                QMessageBox.warning(self, "Partial Load", msg)
        else:
            self.models_info_label.setText("No models loaded")
            self.statusbar.showMessage("No models loaded")
            self.status_label.setText("Status: No models")
            QMessageBox.critical(
                self,
                "No Models",
                "No models could be loaded. Please check your model files."
            )

    def get_active_models(self):
        """Get all loaded models"""
        return self.loaded_models

    def update_zoom(self, value):
        """Update image zoom level"""
        self.zoom_level = value
        self.zoom_label.setText(f"Zoom: {value}%")
        
        if self.current_pixmap:
            self.display_zoomed_image()

    def display_zoomed_image(self):
        """Display image with current zoom level"""
        if not self.current_pixmap:
            return
        
        # Calculate new size based on zoom level
        original_size = self.current_pixmap.size()
        new_width = int(original_size.width() * self.zoom_level / 100)
        new_height = int(original_size.height() * self.zoom_level / 100)
        
        # Scale the pixmap
        scaled_pixmap = self.current_pixmap.scaled(
            new_width, new_height, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.adjustSize()

    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.zoom_slider.setValue(100)

    def fit_to_window(self):
        """Fit image to window size"""
        if not self.current_pixmap:
            return
        
        # Calculate zoom to fit in scroll area
        scroll_size = self.scroll_area.size()
        pixmap_size = self.current_pixmap.size()
        
        width_ratio = (scroll_size.width() - 10) / pixmap_size.width()
        height_ratio = (scroll_size.height() - 10) / pixmap_size.height()
        
        zoom = min(width_ratio, height_ratio) * 100
        zoom = max(10, min(300, int(zoom)))  # Clamp between 10% and 300%
        
        self.zoom_slider.setValue(zoom)

    def init_ui(self):
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open Image...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.upload_image)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(lambda: self.zoom_slider.setValue(self.zoom_level + 10))
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(lambda: self.zoom_slider.setValue(self.zoom_level - 10))
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("Reset Zoom", self)
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
        fit_action = QAction("Fit to Window", self)
        fit_action.setShortcut("Ctrl+F")
        fit_action.triggered.connect(self.fit_to_window)
        view_menu.addAction(fit_action)
        
        # Model menu
        model_menu = menubar.addMenu("Model")
        
        reload_action = QAction("Reload All Models", self)
        reload_action.triggered.connect(self.reload_all_models)
        model_menu.addAction(reload_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Title section
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #000080;
                border: 2px solid;
                border-color: #ffffff #000000 #000000 #ffffff;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 8, 10, 8)
        
        title = QLabel("Multi-Model Bacteria Colony Detection System v2.0")
        title.setStyleSheet("""
            font-family: 'MS Sans Serif', sans-serif;
            font-size: 14px;
            font-weight: bold;
            color: #ffffff;
            background-color: transparent;
        """)
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        main_layout.addWidget(title_frame)

        # Model info group
        model_group = Windows95GroupBox("Loaded Models (All models run automatically)")
        model_layout = QVBoxLayout(model_group)
        model_layout.setContentsMargins(10, 20, 10, 10)
        
        self.models_info_label = QLabel("Loading models...")
        self.models_info_label.setStyleSheet("padding: 5px; font-weight: bold;")
        
        model_layout.addWidget(self.models_info_label)
        
        main_layout.addWidget(model_group)

        # Button panel
        button_group = Windows95GroupBox("Actions")
        button_layout = QHBoxLayout(button_group)
        button_layout.setContentsMargins(10, 20, 10, 10)
        
        self.upload_btn = QPushButton("Open Image & Detect")
        self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.clicked.connect(self.upload_image)
        self.upload_btn.setFixedWidth(150)
        
        button_layout.addWidget(self.upload_btn)
        button_layout.addStretch()
        
        main_layout.addWidget(button_group)

        # Content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(8)

        # Left side - Image display with zoom controls
        image_group = Windows95GroupBox("Detection Results")
        image_layout = QVBoxLayout(image_group)
        image_layout.setContentsMargins(10, 20, 10, 10)
        
        # Zoom controls
        zoom_controls = QFrame()
        zoom_controls.setStyleSheet("""
            QFrame {
                background-color: #c0c0c0;
                border: 2px solid;
                border-color: #808080 #ffffff #ffffff #808080;
                padding: 5px;
            }
        """)
        zoom_layout = QHBoxLayout(zoom_controls)
        zoom_layout.setContentsMargins(5, 5, 5, 5)
        
        self.zoom_label = QLabel("Zoom: 100%")
        self.zoom_label.setStyleSheet("font-weight: bold; border: none;")
        self.zoom_label.setFixedWidth(80)
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(300)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider.setTickInterval(50)
        self.zoom_slider.valueChanged.connect(self.update_zoom)
        
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedSize(30, 25)
        zoom_out_btn.clicked.connect(lambda: self.zoom_slider.setValue(self.zoom_level - 10))
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(30, 25)
        zoom_in_btn.clicked.connect(lambda: self.zoom_slider.setValue(self.zoom_level + 10))
        
        reset_btn = QPushButton("Reset")
        reset_btn.setFixedWidth(60)
        reset_btn.clicked.connect(self.reset_zoom)
        
        fit_btn = QPushButton("Fit")
        fit_btn.setFixedWidth(60)
        fit_btn.clicked.connect(self.fit_to_window)
        
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(zoom_out_btn)
        zoom_layout.addWidget(self.zoom_slider)
        zoom_layout.addWidget(zoom_in_btn)
        zoom_layout.addWidget(reset_btn)
        zoom_layout.addWidget(fit_btn)
        
        image_layout.addWidget(zoom_controls)
        
        # Scroll area for image
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: #ffffff;
            color: #808080;
        """)
        self.image_label.setText("No image loaded.\n\nClick 'Open Image & Detect' to begin.")
        self.image_label.setMinimumSize(650, 450)
        
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setFixedSize(650, 450)
        
        image_layout.addWidget(self.scroll_area)
        
        content_layout.addWidget(image_group, 2)

        # Right side - Statistics
        stats_group = Windows95GroupBox("Detection Information")
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.setContentsMargins(10, 20, 10, 10)
        stats_layout.setSpacing(10)
        
        # Statistics frame
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #c0c0c0;
                border: 2px solid;
                border-color: #808080 #ffffff #ffffff #808080;
                padding: 10px;
            }
        """)
        stats_inner_layout = QVBoxLayout(stats_frame)
        stats_inner_layout.setSpacing(8)
        
        self.models_used_label = QLabel("Models Used: 0")
        self.models_used_label.setStyleSheet("font-weight: bold; padding: 3px; color: #000080;")
        
        self.total_label = QLabel("Total Colonies: 0")
        self.total_label.setStyleSheet("font-weight: bold; padding: 3px;")
        
        self.confidence_label = QLabel("Average Confidence: 0%")
        self.confidence_label.setStyleSheet("font-weight: bold; padding: 3px;")
        
        self.overall_detection_label = QLabel("Overall Detection: 0.00%")
        self.overall_detection_label.setStyleSheet("font-weight: bold; padding: 3px; color: #008000;")
        
        self.time_label = QLabel("Processing Time: 0.00s")
        self.time_label.setStyleSheet("font-weight: bold; padding: 3px;")
        
        stats_inner_layout.addWidget(self.models_used_label)
        stats_inner_layout.addWidget(self.total_label)
        stats_inner_layout.addWidget(self.confidence_label)
        stats_inner_layout.addWidget(self.overall_detection_label)
        stats_inner_layout.addWidget(self.time_label)
        stats_inner_layout.addStretch()
        
        stats_layout.addWidget(stats_frame)
        
        # Details text area
        details_label = QLabel("Details:")
        details_label.setStyleSheet("font-weight: bold; padding: 5px 0;")
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFixedHeight(220)
        self.details_text.setText("No detection results available.\n\nLoad an image and run detection to see detailed analysis.")
        
        stats_layout.addWidget(details_label)
        stats_layout.addWidget(self.details_text)
        
        content_layout.addWidget(stats_group, 1)
        
        main_layout.addLayout(content_layout)

        # Status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")
        
        self.status_label = QLabel("Status: Idle")
        self.status_label.setStyleSheet("""
            border: 2px solid;
            border-color: #808080 #ffffff #ffffff #808080;
            padding: 2px 8px;
            margin-right: 5px;
        """)
        self.statusbar.addPermanentWidget(self.status_label)

    def reload_all_models(self):
        """Reload all models"""
        reply = QMessageBox.question(
            self,
            "Reload Models",
            "This will reload all model files. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.loaded_models.clear()
            self.load_all_models()

    def upload_image(self):
        active_models = self.get_active_models()
        
        if not active_models:
            QMessageBox.warning(
                self,
                "No Models Loaded",
                "No models are loaded. Please check your model files and restart."
            )
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image File",
            "",
            "Image Files (*.jpg *.jpeg *.png *.bmp)"
        )
        if not file_path:
            return

        # Update status
        self.status_label.setText("Status: Processing...")
        self.upload_btn.setEnabled(False)
        self.statusbar.showMessage(f"Processing with {len(active_models)} model(s)...")
        QApplication.processEvents()

        import time
        start_time = time.time()

        try:
            # Load image to get dimensions
            img = cv2.imread(file_path)
            img_h, img_w = img.shape[:2]
            image_area = img_h * img_w
            
            # Storage for combined results
            all_boxes = []
            all_classes = []
            all_confidences = []
            all_model_names = []
            all_class_names = []
            all_areas = []
            
            model_results = {}
            
            # Run each active model
            for model_name, model in active_models.items():
                self.statusbar.showMessage(f"Running: {model_name}...")
                QApplication.processEvents()
                
                results = model(file_path, conf=0.5)
                detections = results[0]
                
                boxes = detections.boxes.xyxy.cpu().numpy() if detections.boxes is not None else []
                classes = detections.boxes.cls.cpu().numpy().astype(int) if detections.boxes is not None else []
                confidences = detections.boxes.conf.cpu().numpy() if detections.boxes is not None else []
                
                # Calculate areas for this model
                model_areas = []
                for box in boxes:
                    x1, y1, x2, y2 = box
                    area = max(0, x2 - x1) * max(0, y2 - y1)
                    model_areas.append(area)
                
                # Store results for this model
                model_results[model_name] = {
                    'boxes': boxes,
                    'classes': classes,
                    'confidences': confidences,
                    'areas': model_areas,
                    'names': model.names,
                    'count': len(boxes)
                }
                
                # Add to combined results
                for box, cls, conf, area in zip(boxes, classes, confidences, model_areas):
                    all_boxes.append(box)
                    all_classes.append(cls)
                    all_confidences.append(conf)
                    all_model_names.append(model_name)
                    all_class_names.append(model.names[cls])
                    all_areas.append(area)

            # Calculate overall stats
            total_detections = len(all_boxes)
            avg_confidence = np.mean(all_confidences) * 100 if len(all_confidences) > 0 else 0
            total_detected_area = sum(all_areas)
            overall_detection_percent = 100 * total_detected_area / image_area if image_area > 0 else 0

            # Calculate percentage by count for each class
            counts_per_class = {}
            areas_per_class = {}
            for cls_name, area in zip(all_class_names, all_areas):
                counts_per_class[cls_name] = counts_per_class.get(cls_name, 0) + 1
                areas_per_class[cls_name] = areas_per_class.get(cls_name, 0) + area
            
            counts_pct = {name: 100 * count / total_detections if total_detections > 0 else 0 
                         for name, count in counts_per_class.items()}
            areas_pct = {name: 100 * area / total_detected_area if total_detected_area > 0 else 0 
                        for name, area in areas_per_class.items()}

            # Draw all detections on image
            # Different colors for different models
            available_colors = [
                (0, 255, 0),      # Green
                (255, 0, 0),      # Blue
                (0, 255, 255),    # Yellow
                (255, 0, 255),    # Magenta
                (255, 128, 0),    # Orange
                (128, 0, 255),    # Purple
                (0, 128, 255),    # Light Blue
                (255, 255, 0),    # Cyan
            ]
            
            # Assign colors to models
            model_colors = {}
            for i, model_name in enumerate(active_models.keys()):
                model_colors[model_name] = available_colors[i % len(available_colors)]
            
            # Draw all detections
            for box, cls, conf, model_name, class_name, area in zip(
                all_boxes, all_classes, all_confidences, all_model_names, all_class_names, all_areas
            ):
                x1, y1, x2, y2 = map(int, box)
                color = model_colors.get(model_name, (0, 255, 0))
                
                # Calculate area percentage for this box
                box_area_pct = 100 * (area / total_detected_area) if total_detected_area > 0 else 0
                
                # Draw rectangle
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                
                # Label with class and area percentage
                text = f"{class_name}: {box_area_pct:.1f}%"
                (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                
                # Background for text
                cv2.rectangle(img, (x1, y1 - text_h - 6), (x1 + text_w + 4, y1), color, -1)
                cv2.putText(img, text, (x1 + 2, y1 - 4),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Save result
            output_path = "detected_result_combined.jpg"
            cv2.imwrite(output_path, img)

            # Display image with zoom
            self.current_pixmap = QPixmap(output_path)
            self.reset_zoom()  # Reset to 100% zoom
            
            # Update stats
            process_time = time.time() - start_time
            self.models_used_label.setText(f"Models Used: {len(active_models)}")
            self.total_label.setText(f"Total Colonies: {total_detections}")
            self.confidence_label.setText(f"Average Confidence: {avg_confidence:.1f}%")
            self.overall_detection_label.setText(f"Overall Detection: {overall_detection_percent:.2f}% of image")
            self.time_label.setText(f"Processing Time: {process_time:.2f}s")

            # Build detailed results text
            details_text = "=" * 50 + "\n"
            details_text += "MULTI-MODEL DETECTION SUMMARY\n"
            details_text += "=" * 50 + "\n\n"
            details_text += f"Total Models Run: {len(active_models)}\n"
            details_text += f"Total Detections: {total_detections}\n"
            details_text += f"Average Confidence: {avg_confidence:.2f}%\n"
            details_text += f"Overall Detection: {overall_detection_percent:.2f}% of image\n"
            details_text += f"Processing Time: {process_time:.2f}s\n\n"
            
            # Detection-based Bacterial Percentages
            details_text += "=" * 50 + "\n"
            details_text += "📊 DETECTION-BASED BACTERIAL PERCENTAGES PER CLASS\n"
            details_text += "=" * 50 + "\n\n"
            
            details_text += "By Count (Detection Frequency):\n"
            details_text += "-" * 30 + "\n"
            for class_name in sorted(counts_pct.keys()):
                count = counts_per_class[class_name]
                pct = counts_pct[class_name]
                details_text += f"  {class_name}: {count} detections ({pct:.2f}%)\n"
            
            details_text += "\nBy Area (Coverage):\n"
            details_text += "-" * 30 + "\n"
            for class_name in sorted(areas_pct.keys()):
                pct = areas_pct[class_name]
                details_text += f"  {class_name}: {pct:.2f}% of total detected area\n"
            
            details_text += "\n"
            
            # Per-model breakdown
            details_text += "=" * 50 + "\n"
            details_text += "RESULTS BY MODEL\n"
            details_text += "=" * 50 + "\n\n"
            
            for model_name, results in model_results.items():
                details_text += f"[{model_name}]\n"
                details_text += f"  Total: {results['count']} colonies\n"
                
                if results['count'] > 0:
                    # Class breakdown for this model
                    class_counts = {}
                    class_areas = {}
                    for cls, area in zip(results['classes'], results['areas']):
                        class_name = results['names'][cls]
                        class_counts[class_name] = class_counts.get(class_name, 0) + 1
                        class_areas[class_name] = class_areas.get(class_name, 0) + area
                    
                    model_total_area = sum(results['areas'])
                    
                    details_text += "  By Count:\n"
                    for class_name, count in class_counts.items():
                        percentage = (count / results['count'] * 100)
                        details_text += f"    - {class_name}: {count} ({percentage:.1f}%)\n"
                    
                    details_text += "  By Area:\n"
                    for class_name, area in class_areas.items():
                        percentage = (area / model_total_area * 100) if model_total_area > 0 else 0
                        details_text += f"    - {class_name}: {percentage:.1f}%\n"
                
                details_text += "\n"
            
            self.details_text.setText(details_text)

            # Show completion message
            self.show_detection_complete(active_models, model_results, total_detections, overall_detection_percent)
            
            self.statusbar.showMessage(f"Complete - {total_detections} total colonies from {len(active_models)} models")
            self.status_label.setText("Status: Complete")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{str(e)}")
            self.statusbar.showMessage("Error occurred")
            self.status_label.setText("Status: Error")
        
        finally:
            self.upload_btn.setEnabled(True)

    def show_detection_complete(self, active_models, model_results, total, overall_pct):
        msg = QMessageBox(self)
        msg.setWindowTitle("Multi-Model Detection Complete")
        msg.setIcon(QMessageBox.Information)
        
        text = f"Detection Complete!\n\n"
        text += f"Models Run: {len(active_models)}\n"
        text += f"Total Colonies: {total}\n"
        text += f"Overall Detection: {overall_pct:.2f}% of image\n\n"
        text += "Results by model:\n"
        
        for model_name, results in model_results.items():
            text += f"  {model_name}: {results['count']} colonies\n"
        
        msg.setText(text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #c0c0c0;
            }
            QLabel {
                color: #000000;
                font-family: 'MS Sans Serif', sans-serif;
                font-size: 11px;
                min-width: 350px;
            }
            QPushButton {
                background-color: #c0c0c0;
                border: 2px solid;
                border-color: #ffffff #000000 #000000 #ffffff;
                padding: 5px 20px;
                font-weight: bold;
                min-width: 75px;
                min-height: 23px;
            }
            QPushButton:pressed {
                border-color: #000000 #ffffff #ffffff #000000;
            }
        """)
        msg.exec_()

    def show_about(self):
        about_text = "Multi-Model Bacteria Colony Detection\nVersion 2.0\n\n"
        about_text += "Powered by YOLOv8 Deep Learning\n\n"
        about_text += f"Total Models Available: {len(self.model_definitions)}\n"
        about_text += f"Currently Loaded: {len(self.loaded_models)}\n\n"
        about_text += "This version runs multiple models simultaneously\n"
        about_text += "to detect different types of bacteria.\n\n"
        about_text += "Features:\n"
        about_text += "- Detection-based percentage analysis\n"
        about_text += "- By count and by area calculations\n"
        about_text += "- Overall image coverage metrics\n"
        about_text += "- Image zoom and pan support\n\n"
        about_text += "(c) 2025 All Rights Reserved"
        
        QMessageBox.about(self, "About", about_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set Windows 95 palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(192, 192, 192))
    palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(192, 192, 192))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.Button, QColor(192, 192, 192))
    palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.Highlight, QColor(0, 0, 128))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = BacteriaDetector()
    window.show()
    sys.exit(app.exec_())