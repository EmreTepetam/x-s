import os
import subprocess
import tempfile
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QProgressBar, QLabel, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, QSize, QTimer, QPropertyAnimation
from PyQt6.QtGui import QPixmap, QIcon, QPalette, QLinearGradient, QBrush, QColor


class DriverInstallerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Driver Yükleyici")
        self.setGeometry(100, 100, 600, 400)

        # Main Layout
        main_layout = QVBoxLayout()

        # Top Layout for Title and Language Button
        top_layout = QHBoxLayout()

        # Title Label
        self.title_label = QLabel("Driver Yükleyici", self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
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

        # Logo
        self.logo_label = QLabel(self)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.join(os.getcwd(), "resources/logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            self.logo_label.setPixmap(pixmap)
            self.logo_label.setScaledContents(True)
            self.logo_label.setFixedSize(200, 200)  # Başlangıç boyutu
        else:
            self.logo_label.setText("Logo Bulunamadı")
            self.logo_label.setStyleSheet("color: red; font-size: 12px;")
        main_layout.addWidget(self.logo_label)

        # Start Logo Animation
        self.start_logo_animation()

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

        # Gradient Animation
        self.gradient_colors = [(239, 239, 239), (137, 208, 249), (51, 51, 51)]  # Renkler: kırmızı, yeşil, mavi
        self.current_color_index = 0
        self.next_color_index = 1
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_background)
        self.timer.start(50)  # 50ms'de bir güncelle

        # Başlangıç rengi
        self.current_color = self.gradient_colors[self.current_color_index]
        self.next_color = self.gradient_colors[self.next_color_index]
        self.transition_step = 0



    def update_background(self):
        # Geçiş oranını artır
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
        palette = self.palette()
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(r, g, b))
        gradient.setColorAt(1, QColor(255 - r, 255 - g, 255 - b))  # Zıt renk
        brush = QBrush(gradient)
        palette.setBrush(QPalette.ColorRole.Window, brush)
        self.setPalette(palette)

    def start_logo_animation(self):
        """Logoya bir büyütme/küçültme animasyonu ekler."""
        self.animation = QPropertyAnimation(self.logo_label, b"size")
        self.animation.setDuration(1000)  # 1 saniyede bir döngü
        self.animation.setStartValue(QSize(200, 200))  # Başlangıç boyutu
        self.animation.setEndValue(QSize(220, 220))  # Büyütülmüş boyut
        self.animation.setLoopCount(-1)  # Sonsuz döngü
        self.animation.start()

    def toggle_language(self):
        if self.is_turkish:
            self.title_label.setText("Driver Installer")
            self.install_button.setText("Install Driver")
            self.language_button.setIcon(QIcon(os.path.join(os.getcwd(), "resources/en_flag.png")))
            self.is_turkish = False
        else:
            self.title_label.setText("Driver Yükleyici")
            self.install_button.setText("Driver Yükle")
            self.language_button.setIcon(QIcon(os.path.join(os.getcwd(), "resources/tr_flag.png")))
            self.is_turkish = True

    def start_installation(self):
        # Sürücü yükleme işlemi (hatalar ve başarılar burada işlenir)
        pass


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = DriverInstallerApp()
    window.show()
    sys.exit(app.exec())