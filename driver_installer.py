import os
import subprocess
import tempfile
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QProgressBar, QLabel, QWidget, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QPalette, QLinearGradient, QBrush, QColor

class DriverInstallerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Driver Yükleyici")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("color: #333333;")  # Sadece metin için renk

        # Gradient Colors and Timer
        self.gradient_colors = [(255, 255, 255), (173, 216, 230), (176, 224, 230)]  # Beyaz, açık mavi, buz mavisi
        self.current_color_index = 0
        self.next_color_index = 1
        self.transition_step = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_background)
        self.timer.start(50)  # 50ms'de bir güncelleme

        # Başlangıç Renkleri
        self.current_color = self.gradient_colors[self.current_color_index]
        self.next_color = self.gradient_colors[self.next_color_index]

        # Main Layout
        main_layout = QVBoxLayout()

        # Top Layout for Title and Language Button
        top_layout = QHBoxLayout()

        # Title Label
        self.title_label = QLabel("Driver Yükleyici", self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #87CEEB;")
        top_layout.addWidget(self.title_label)

        # Spacer to push language button to the right
        top_layout.addStretch()

        # Language Toggle Button
        self.language_button = QPushButton(self)
        self.language_button.setIcon(QIcon(os.path.join(os.getcwd(), "resources/tr_flag.png")))
        self.language_button.setIconSize(QSize(24, 24))
        self.language_button.setStyleSheet("border: none; position: absolute;")
        self.language_button.setToolTip("Dil Değiştir")
        self.language_button.clicked.connect(self.toggle_language)

        # Add Language Button to Top Layout (Right Aligned)
        top_layout.addWidget(self.language_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Add Top Layout to Main Layout
        main_layout.addLayout(top_layout)

        # Logo Frame
        self.logo_frame = QFrame(self)
        self.logo_frame.setStyleSheet("""
            QFrame {
                background-color: #E0F7FA;
                border-radius: 20px;
                padding: 20px;
                border: 2px solid #0083CA;
            }
        """)
        self.logo_frame.setFixedSize(350, 170)

        # Logo
        self.logo_label = QLabel(self.logo_frame)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.join(os.getcwd(), "resources/logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(QSize(200, 200), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
        else:
            self.logo_label.setText("Logo Bulunamadı")
            self.logo_label.setStyleSheet("color: red; font-size: 12px;")
        self.logo_label.setGeometry(25, 25, 300, 120)

        # Add Logo Frame to Main Layout
        main_layout.addWidget(self.logo_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # Feedback Label (for messages)
        self.feedback_label = QLabel("", self)
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_label.setStyleSheet("font-size: 12px; color: #FF0000;")  # Red for errors
        main_layout.addWidget(self.feedback_label)

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #87CEEB;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #87CEEB;
                width: 20px;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # Install Button
        self.install_button = QPushButton("Driver Yükle", self)
        self.install_button.setStyleSheet("""
            QPushButton {
                background-color: #87CEEB;
                color: white;
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5DADE2;
            }
        """)
        self.install_button.clicked.connect(self.start_installation)
        main_layout.addWidget(self.install_button)

        # Central Widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Language State
        self.is_turkish = True  # Default language is Turkish

    def update_background(self):
        """Arka plan renk geçişini günceller."""
        self.transition_step += 0.01
        if self.transition_step >= 1:
            self.transition_step = 0
            self.current_color_index = self.next_color_index
            self.next_color_index = (self.next_color_index + 1) % len(self.gradient_colors)
            self.current_color = self.gradient_colors[self.current_color_index]
            self.next_color = self.gradient_colors[self.next_color_index]

        # Renkler arasında geçiş yap
        r = int(self.current_color[0] * (1 - self.transition_step) + self.next_color[0] * self.transition_step)
        g = int(self.current_color[1] * (1 - self.transition_step) + self.next_color[1] * self.transition_step)
        b = int(self.current_color[2] * (1 - self.transition_step) + self.next_color[2] * self.transition_step)

        self.set_background_color(r, g, b)

    def set_background_color(self, r, g, b):
        """Arka plan rengini ayarlar."""
        palette = self.palette()
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(r, g, b))
        gradient.setColorAt(1, QColor(255, 255, 255))  # Beyaza doğru geçiş
        brush = QBrush(gradient)
        palette.setBrush(QPalette.ColorRole.Window, brush)
        self.setPalette(palette)

    def toggle_language(self):
        if self.is_turkish:
            # Switch to English
            self.title_label.setText("Driver Installer")
            self.install_button.setText("Install Driver")
            self.language_button.setIcon(QIcon(os.path.join(os.getcwd(), "resources/en_flag.png")))
            self.is_turkish = False
        else:
            # Switch to Turkish
            self.title_label.setText("Driver Yükleyici")
            self.install_button.setText("Driver Yükle")
            self.language_button.setIcon(QIcon(os.path.join(os.getcwd(), "resources/tr_flag.png")))
            self.is_turkish = True

    def start_installation(self):
        drivers_path = os.path.join(os.getcwd(), "drivers")
        if not os.path.exists(drivers_path):
            self.show_feedback("Driver klasörü bulunamadı!", error=True)
            return

        inf_files = [f for f in os.listdir(drivers_path) if f.endswith(".inf")]
        if not inf_files:
            self.show_feedback("Driver klasöründe .inf dosyası bulunamadı!", error=True)
            return

        self.progress_bar.setMaximum(len(inf_files))
        success_count = 0
        failed_files = []

        for i, inf_file in enumerate(inf_files, start=1):
            inf_path = os.path.join(drivers_path, inf_file)
            if self.install_driver(inf_path):
                success_count += 1
            else:
                failed_files.append(inf_file)

            self.progress_bar.setValue(i)

        if failed_files:
            failed_list = ", ".join(failed_files)
            self.show_feedback(f"Aşağıdaki driver(lar) yüklenemedi: {failed_list}", error=True)
        else:
            self.show_feedback(f"Tüm driver yüklemeleri başarıyla tamamlandı! ({success_count}/{len(inf_files)})", error=False)

    def install_driver(self, inf_path):
        temp_dir = tempfile.gettempdir()
        log_file = os.path.join(temp_dir, "driver_installation.log")
        try:
            result = subprocess.run(
                ["pnputil", "/add-driver", inf_path, "/install"],
                capture_output=True,
                text=True,
                check=True
            )
            with open(log_file, "a") as log:
                log.write(f"SUCCESS: {inf_path} yüklendi.\n")
            return True
        except subprocess.CalledProcessError as e:
            with open(log_file, "a") as log:
                log.write(f"ERROR: {inf_path} yüklenemedi.\n{e.stderr}\n")
            return False

    def show_feedback(self, message, error=False):
        """Show feedback above the progress bar."""
        self.feedback_label.setText(message)
        if error:
            self.feedback_label.setStyleSheet("font-size: 12px; color: #FF0000;")  # Red for errors
        else:
            self.feedback_label.setStyleSheet("font-size: 12px; color: #008000;")  # Green for success

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = DriverInstallerApp()
    window.show()
    sys.exit(app.exec())