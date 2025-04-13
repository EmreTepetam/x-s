import os
import subprocess
import tempfile
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QProgressBar, QLabel, QWidget, QHBoxLayout, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QPalette, QLinearGradient, QBrush, QColor

class DriverInstallerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.translations = self.load_translations()
        self.current_language = "tr"  # Varsayılan dil
        self.setWindowTitle(self.translations["title_name"][self.current_language])
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("color: #333333;")  # Sadece metin için renk
        # Main Layout
        main_layout = QVBoxLayout()

        # Gradient Background Animation
        self.gradient_colors = [(179, 217, 255), (102, 179, 255), (230, 242, 255)]  # Açık mavi tonları
        self.current_color_index = 0
        self.next_color_index = 1
        self.transition_step = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_background)
        self.timer.start(50)  # 50ms'de bir güncelleme
        self.current_color = self.gradient_colors[self.current_color_index]
        self.next_color = self.gradient_colors[self.next_color_index]



        # Top Layout for Title and Language Button
        top_layout = QHBoxLayout()

        # Spacer to push language button to the right
        top_layout.addStretch()

        # Language Toggle Button
        self.language_button = QPushButton(self)
        self.language_button.setIcon(QIcon(os.path.join(os.getcwd(), "resources/tr_flag.png")))
        self.language_button.setIconSize(QSize(24, 24))
        self.language_button.setStyleSheet("border: none; position: absolute;")
        self.language_button.setToolTip("Dil Değiştir")
        self.language_button.clicked.connect(self.toggle_language)
        top_layout.addWidget(self.language_button, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(top_layout)


        # Logo with Glassmorphism
        self.logo_label = QLabel(self)
        self.logo_label.setFixedSize(200, 200)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setStyleSheet("""
            QLabel {
                background: rgba(176, 220, 255, 0.4);  /* Glassmorphism efekti */
                border-radius: 100px;  /* Yuvarlak logo */
                border: 1px solid rgba(198, 230, 255, 0.3);  /* Kenar rengi */
            }
        """)

        glow_effect = QGraphicsDropShadowEffect(self)
        glow_effect.setBlurRadius(40)  # Glow'un bulanıklık seviyesi
        glow_effect.setColor(QColor(210, 239, 255))  # Glow rengi (açık mavi)
        glow_effect.setOffset(0, 0)  # Gölgenin pozisyonu (merkezlenmiş)
        self.logo_label.setGraphicsEffect(glow_effect)

        # Logo Image
        logo_path = os.path.join(os.getcwd(), "resources/logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.setText("Logo Bulunamadı")
            self.logo_label.setStyleSheet("color: red; font-size: 12px;")
        main_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Driver Name Label (Sabit sürücü adı gösterimi)
        self.driver_name_label = QLabel(self.translations["driver_name"][self.current_language], self)
        self.driver_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.driver_name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333;")
        main_layout.addWidget(self.driver_name_label)

        # Feedback Label (for messages)
        self.feedback_label = QLabel("", self)
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_label.setStyleSheet("font-size: 12px; color: #FF0000;")  # Red for errors
        main_layout.addWidget(self.feedback_label)

        # Progress Bar Timer
        self.progress_value = 0
        self.progress_target = 0  # Target value for progress bar
        self.progress_message = ""  # Message to show after progress completes
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress_bar)


        # Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #87CEEB;
                border-radius: 5px;
                text-align: center;
                text-color: #313131;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #87CEEB;
                width: 20px;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # Install Button
        self.install_button = QPushButton(self.translations["install_button"][self.current_language], self)
        self.install_button.setStyleSheet("""
            QPushButton {
                background-color: #87CEEB;
                color: #333333;
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

    def load_translations(self):
            """Dil çevirilerini JSON dosyasından yükler."""
            json_path = os.path.join(os.getcwd(), "drivers", "driver_name.json")
            try:
                with open(json_path, "r", encoding="utf-8") as file:
                    return json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                return {
                    "driver_name": {"tr": "Bilinmeyen Sürücü", "en": "Unknown Driver"},
                    "install_button": {"tr": "Sürücü Yükle", "en": "Install Driver"},
                    "loading_message": {"tr": "Yükleme başlatıldı...", "en": "Installation started..."},
                    "success_message": {"tr": "Yükleme başarılı!", "en": "Installation successful!"},
                    "error_message": {"tr": "Yükleme sırasında hata oluştu.",
                                      "en": "An error occurred during installation."}
                }

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
    def update_progress_bar(self):
        """
        Simulates progress bar increments.
        """
        if self.progress_value < self.progress_target:
            self.progress_value += 5
            self.progress_bar.setValue(self.progress_value)
        else:
            self.progress_timer.stop()
            self.show_feedback(self.progress_message, error=False)

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
        """Dil değiştirir ve arayüzü günceller."""
        self.current_language = "en" if self.current_language == "tr" else "tr"
        self.language_button.setIcon(
            QIcon(os.path.join(os.getcwd(), "resources/en_flag.png" if self.current_language == "en" else "resources/tr_flag.png"))
        )
        self.update_language()
    def update_language(self):
        """Arayüzdeki tüm metinleri seçilen dile göre günceller."""
        self.setWindowTitle(self.translations["title_name"][self.current_language])
        self.driver_name_label.setText(self.translations["driver_name"][self.current_language])
        self.install_button.setText(self.translations["install_button"][self.current_language])
    def get_driver_name(self):
        """
        JSON dosyasından driver adını okur.
        """
        json_path = os.path.join(os.getcwd(), "drivers", "driver_name.json")
        try:
            with open(json_path, "r", encoding="utf-8") as json_file:
                driver_name = json.load(json_file)
                language = "tr" if self.is_turkish else "en"
                return driver_name.get(language, "Bilinmeyen Driver")
        except (FileNotFoundError, json.JSONDecodeError):
            return "Bilinmeyen Driver"
    def start_installation(self):
        """
        Driver yükleme işlemini başlatır.
        """
        drivers_path = os.path.join(os.getcwd(), "drivers")  # drivers klasörü yolu
        if not os.path.exists(drivers_path):  # Klasör var mı kontrol et
            self.feedback_label.setText(self.translations["loading_message"][self.current_language])
            self.progress_bar.setValue(0)
            return

        inf_files = [f for f in os.listdir(drivers_path) if f.endswith(".inf")]  # Tüm .inf dosyalarını bul
        if not inf_files:  # Hiç .inf dosyası yoksa hata
            self.feedback_label.setText(self.translations["success_message"][self.current_language])
            self.progress_bar.setValue(0)
            return

        # Sadece ilk .inf dosyasını al
        inf_file = inf_files[0]
        inf_path = os.path.join(drivers_path, inf_file)  # Dosya yolunu birleştir

        self.progress_value = 0
        self.progress_bar.setValue(0)
        self.feedback_label.setText(self.translations["loading_message"][self.current_language])

        # Start the installation process and determine the outcome
        success, message = self.install_driver(inf_path)


        if success:
            if "zaten sistemde mevcut" in message:
                self.progress_target = 50  # Set target for progress bar
                self.progress_message = message
                self.progress_timer.start(50)  # Increment progress bar
            else:
                self.progress_target = 100  # Set target for progress bar
                self.feedback_label.setText(self.translations["loading_message"][self.current_language])
                self.progress_timer.start(50)  # Increment progress bar
        else:
            self.progress_bar.setValue(0)  # Reset progress bar on error
            self.show_feedback(message, error=True)
            self.show_feedback(message, error=True)
    def install_driver(self, inf_path):
        """
        Driver yükleme işlemini gerçekleştirir.
        """
        temp_dir = tempfile.gettempdir()
        log_file = os.path.join(temp_dir, "driver_installation.log")
        try:
            # Komutu çalıştır
            result = subprocess.run(
                ["pnputil", "/add-driver", inf_path, "/install"],
                capture_output=True,
                text=True,
            )

            # Çıktıları al
            stdout_output = result.stdout.strip()
            stderr_output = result.stderr.strip()

            # Başarı kontrolü
            if "Driver package added successfully." in stdout_output:
                if "(Already exists in the system)" in stdout_output:
                    return True, self.translations["already_exists_message"][self.current_language].format(driver_name=os.path.basename(inf_path))
                return True, self.translations["success_message"][self.current_language].format(driver_name=os.path.basename(inf_path))

            # Hata kontrolü
            error_message = stderr_output or self.translations["error_message"][self.current_language]
            return False, self.translations["error_message"][self.current_language].format(driver_name=os.path.basename(inf_path), error_message=error_message)

        except Exception as e:
            error_message = self.translations["unexpected_error_message"][self.current_language].format(
                driver_name=os.path.basename(inf_path),
                error_details=str(e)
            )
            return False, error_message

    def show_feedback(self, message, error=False):
        """
        Kullanıcıya mesaj gösterir.
        """
        self.feedback_label.setText(message)
        self.feedback_label.setStyleSheet(
            "font-size: 12px; color: #FF0000;" if error else "font-size: 12px; color: #008000;"
        )
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = DriverInstallerApp()
    window.show()
    sys.exit(app.exec())