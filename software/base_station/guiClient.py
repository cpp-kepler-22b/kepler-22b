### Keppler-22b Ground Station GUI Client ###
### Engineer: Aman Adhikari ###
### Date: 10/15/2021 ###

import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow,QDialog, QFileDialog, QTabWidget, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QInputDialog, QHBoxLayout, QTextEdit)
from PySide6.QtGui import QAction, QFont, QIcon, QPixmap
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtGui import QImage, QPixmap
from threading import Thread
import asyncio
import websockets
from skyfield.api import load, Topos
from skyfield.data import hipparcos
from functools import partial
from classes.vidServer import vidServer
from classes.messageServer import sendCommand
from classes.receiveMsg import receiveMessage
import cv2
import threading
import time



#### Preset HIP numbers for constellations ####
constellation_presets = {
    'Alpha Andromedae': 677,     # Alpheratz (Alpha Andromedae)
    'Aquarius': 106278,   # Sadalmelik (Alpha Aquarii)
    'Aries': 9884,        # Hamal (Alpha Arietis)
    'Cancer': 43103,      # Al Tarf (Beta Cancri)
    'Canis Major': 32349, # Sirius (Alpha Canis Majoris)
    'Capricornus': 107556,# Deneb Algedi (Delta Capricorni)
    'Cassiopeia': 3179,   # Schedar (Alpha Cassiopeiae)
    'Cygnus': 102098,     # Deneb (Alpha Cygni)
    'Gemini': 37826,      # Pollux (Beta Geminorum)
    'Leo': 49669,         # Regulus (Alpha Leonis)
    'Libra': 72622,       # Zubeneschamali (Beta Librae)
    'Lyra': 91262,        # Vega (Alpha Lyrae)
    'Alpha Orionis': 26727,       # Betelgeuse (Alpha Orionis)
    'Epsilon Pegasi': 113963,    # Enif (Epsilon Pegasi)
    'Eta Piscium': 9487,       # Alpherg (Eta Piscium)
    'Epsilon Sagittarii': 88635, # Kaus Australis (Epsilon Sagittarii)
    'Alpha Scorpii': 80763,    # Antares (Alpha Scorpii)
    'Alpha Tauri': 21421,      # Aldebaran (Alpha Tauri)
    'Alpha Ursae Majoris': 54061,  # Dubhe (Alpha Ursae Majoris)
    'Alpha Ursae Minoris': 11767,  # Polaris (Alpha Ursae Minoris)
    'Virgo': 65474,       # Spica (Alpha Virginis)
}



#### Websocket Client ####



### Main Application Window ###
class StarFinderGUI(QMainWindow):
    def __init__(self, stars):
        
        ###MainWindow###
        super().__init__()
        
        self.setWindowTitle("Keppler-22b Ground Station")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("nasa.png"))
        self.stars = stars
        
        ### Stlyesheets ###
        self.isDarkMode = True  # Default to dark mode
        self.isStarViewMode = False  # Star view mode off by default
        self.dark_stylesheet = """
        QWidget, QLineEdit, QTextEdit, QPushButton, QLabel, QMenuBar, QMenu, QTabWidget, QDialog, QTabBar::tab {
            color: white; 
            background-color: #333; 
            font: 14px; 
        }
        QPushButton { 
            background-color: #555; 
            color: white; 
        }
        QLineEdit, QTextEdit { 
            background-color: #555; 
            color: white; 
        }
        QLabel { 
            color: #CCC; 
        }
        QLabel#imageLabel { /* Target the image viewer specifically */
            border: 2px solid #AAA; /* Added a light gray border */
            color: #CCC;
            padding: 2px; /* Added padding inside the border */
        }
        QTabWidget::pane { /* The tab widget frame */
            border-top: 2px solid #555;
        }
        QTabBar::tab:selected { /* The selected tab */
            background: #777;
            margin-top: 2px;
            padding: 4px;
            font-size: 14px;
        }
        QTabBar::tab:!selected { /* Unselected tabs */
            background: #555;
            margin-top: 2px;
            padding: 4px;
            font-size: 14px;
        }
        QMenu::item {
            background-color: transparent;
            color: white;
        }
        QMenu::item:selected {
            background-color: #0078d7;
            color: white;
        }
        """
        self.light_stylesheet = """
        QWidget, QLineEdit, QTextEdit, QPushButton, QLabel, QMenuBar, QMenu, QTabWidget, QDialog {
            color: black; 
            background-color: #FFF; 
            font: 14px;
        }
        QPushButton { 
            background-color: #DDD; 
            color: black; 
        }
        QLineEdit, QTextEdit { 
            background-color: #EEE; 
            color: black; 
        }
        QLabel { 
            color: #333; 
        }
        QTabBar::tab:selected { /* The selected tab */
            background: #FFF;
            border: 1px solid #CCC;
            border-bottom-color: #FFF; /* Makes the bottom border invisible */
            margin-top: 2px;
            padding: 4px;
            font-size: 14px;
        }
        QTabBar::tab:!selected { /* Unselected tabs */
            background: #DDD;
            border: 1px solid #CCC;
            margin-top: 2px;
            padding: 4px;
            font-size: 14px;
        }
        QMenu::item {
            background-color: transparent;
            color: black;
        }
        QMenu::item:selected {
            background-color: #0078d7;
            color: white;
        }
        """
        self.star_view_stylesheet = """
        QWidget, QLineEdit, QTextEdit, QPushButton, QLabel, QMenuBar, QMenu, QTabWidget, QDialog {
            background-color: #300; 
            color: #F00; 
            font: 14px; 
        }
        QPushButton { 
            background-color: #400; 
            color: #F00; 
        }
        QLineEdit, QTextEdit { 
            background-color: #400; 
            color: #F00; 
        }
        QLabel { 
            color: #F00; 
        }
        QMenu::item {
            background-color: transparent;
            color: #F00;
        }
        QMenu::item:selected {
            background-color: #700;
            color: #FFF;
        }
        """
        self.setStyleSheet(self.dark_stylesheet)
        self.tabWidget = QTabWidget(self)
        self.setCentralWidget(self.tabWidget)
        self.toggleMode()

        ### Server Connection Popup ###
        self.server_ip, ok = QInputDialog.getText(self, 'WebSocket Server IP', 'Enter WebSocket server IP:')
        if ok and self.server_ip:
            self.initUI()
            self.start_websocket_client(self.server_ip)
        else:
            sys.exit()
        
        


            
    def toggleMode(self):
        # This function toggles the theme between light and dark mode
        if self.isStarViewMode:
            self.setStyleSheet(self.star_view_stylesheet)
            self.isStarViewMode = False
        elif self.isDarkMode:
            self.setStyleSheet(self.light_stylesheet)
        else:
            self.setStyleSheet(self.dark_stylesheet)
        self.isDarkMode = not self.isDarkMode
    def toggleStarViewMode(self):
        if not self.isStarViewMode:
            self.setStyleSheet(self.star_view_stylesheet)
        else:
            # Reverts respective theme when exiting star view mode
            self.setStyleSheet(self.dark_stylesheet if self.isDarkMode else self.light_stylesheet)
        self.isStarViewMode = not self.isStarViewMode

    def initUI(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        ###Main Outer Layout###
        main_layout = QHBoxLayout(central_widget)

        ### TABS ###  
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab1, "Camera View")
        self.tabs.addTab(self.tab2, "Image Viewer")

        main_layout.addWidget(self.tabs)

        self.tab1UI()
        self.tab2UI()

        # Right panel with controls and star finder, using NASA color theme
        right_panel = QVBoxLayout()

        self.initMenuBar()

        # Input for star HIP number
        self.starInput = QLineEdit(self)
        self.starInput.setStyleSheet("font: 14px; padding: 5px;")
        right_panel.addWidget(self.starInput)

        self.findButton = QPushButton("Find Star", self)
        self.findButton.setStyleSheet("background-color: #14213d; color: white; padding: 10px;")
        self.findButton.clicked.connect(self.find_star)
        right_panel.addWidget(self.findButton)

        self.starNameLabel = QLabel("", self)
        self.starNameLabel.setStyleSheet("color: #3498DB;")
        right_panel.addWidget(self.starNameLabel) # Star name label

        self.resultLabel = QLabel("", self)
        self.resultLabel.setStyleSheet("color: #3498DB;")
        right_panel.addWidget(self.resultLabel) # Celstian Cordinates label

        self.altAzLabel = QLabel("", self)
        self.altAzLabel.setStyleSheet("color: #3498DB;")
        right_panel.addWidget(self.altAzLabel) # Altitude/Azimuth Cordinates label

        ### Console  server messages ###
        self.console = QTextEdit(self)
        self.console.setStyleSheet("background-color: #e5e5e5; color: black;")
        self.console.setReadOnly(True)
        self.console.setPlaceholderText("Server messages will appear here...")
        right_panel.addWidget(self.console)

        ### User message input ###
        self.userMessageInput = QLineEdit(self)
        self.userMessageInput.setStyleSheet("font: 14px; padding: 5px;")
        right_panel.addWidget(self.userMessageInput)

        ### Send message button ###
        self.sendButton = QPushButton("Send Message to Server", self)
        self.sendButton.setStyleSheet("background-color: #14213d; color: white; padding: 10px;")
        self.sendButton.clicked.connect(self.send_message_to_server)
        right_panel.addWidget(self.sendButton)

        ### Add panel layout to main layout ###
        main_layout.addLayout(right_panel)

    #def initTelescope
    def initTelescopeCam(self):
        self.videoStreamLabel = QLabel("LIVE CAMERA VIEW WILL GO HERE")

        # Set up a QTimer to update the image
        self.timer = QTimer()
        self.timer.setInterval(10)  # Update interval in milliseconds
        self.timer.timeout.connect(self.update_image)
        self.timer.start()

    def tab1UI(self):
        layout = QVBoxLayout(self.tab1)
        self.initTelescopeCam()
        layout.addWidget(self.videoStreamLabel)

    def tab2UI(self):
        layout = QVBoxLayout(self.tab2)

        self.image_label = QLabel("No images loaded.", self)
        self.image_label.setObjectName("imageLabel")  # This name should match the one in the stylesheet
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        self.change_dir_button = QPushButton("Change Directory")
        self.change_dir_button.clicked.connect(self.change_directory)
        layout.addWidget(self.change_dir_button)

        nav_layout = QHBoxLayout()
        layout.addLayout(nav_layout)

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.show_previous_image)
        nav_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.show_next_image)
        nav_layout.addWidget(self.next_button)

        self.image_paths = []
        self.current_image_index = 0
    
    def change_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.image_paths = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.current_image_index = 0
            self.show_image()

    def show_image(self):
        if self.image_paths:
            pixmap = QPixmap(self.image_paths[self.current_image_index])
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def show_next_image(self):
        if 0 <= self.current_image_index < len(self.image_paths) - 1:
            self.current_image_index += 1
            self.show_image()

    def show_previous_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.show_image()

    def launch_gallery(self):
        if not hasattr(self, 'galleryWindow') or not self.galleryWindow.isVisible():
            self.galleryWindow = GalleryWindow(self)
        self.galleryWindow.show()
        self.galleryWindow.activateWindow()  # Brings the gallery window to the front

    def initMenuBar(self):
        menu_bar = self.menuBar()

        menu_bar.setStyleSheet("""
        QMenu::item {
        padding: 2px 25px 2px 20px;
        background-color: transparent;
        border: 1px solid transparent;  # Maintain transparent border
    }
    QMenu::item:selected {  # Use :selected for hover and active states
        background-color: #0078d7;  # A noticeable background color on hover
        color: white;  # Change text color for better visibility
    }
    """)


        file_menu = menu_bar.addMenu('File')
        view_menu = menu_bar.addMenu('View')
        tool_menu = menu_bar.addMenu('Tool')

        stars_menu = menu_bar.addMenu('Stars')
        for constellation, hip_num in constellation_presets.items():
            action = QAction(constellation, self)
            action.triggered.connect(partial(self.load_star_by_hip, hip_num, constellation))
            stars_menu.addAction(action)


        toggle_theme_action = QAction('Toggle Light/Dark Mode', self)
        toggle_theme_action.triggered.connect(self.toggleMode)
        view_menu.addAction(toggle_theme_action)

        star_view_mode_action = QAction('Toggle Star View Mode', self)
        star_view_mode_action.triggered.connect(self.toggleStarViewMode)
        view_menu.addAction(star_view_mode_action)

    def update_image(self):
        # Get a new image from the vidServer
        img = self.videoServer.getImg()
        if img is not None:
            # Convert the NumPy array to QImage
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, channels = img.shape
            bytes_per_line = channels * width
            q_image = QImage(img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

            # Convert QImage to QPixmap and display it
            pixmap = QPixmap.fromImage(q_image)
            self.videoStreamLabel.setPixmap(pixmap)

    def captureImage(self):
        image = self.get_current_video_frame()  # Replace with actual frame capture code
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.png"
        image.save(os.path.join(self.images_directory, filename))
        self.updateGallery()
    def createGallery(self):
        self.galleryWidget = QWidget(self)
        self.galleryLayout = QHBoxLayout(self.galleryWidget)
        # Add the left navigation button
        self.prevImageButton = QPushButton("<", self)
        self.prevImageButton.clicked.connect(self.prevImage)
        self.galleryLayout.addWidget(self.prevImageButton)
        # Create a scroll area for thumbnails
        self.scrollArea = QScrollArea(self)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaLayout = QHBoxLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.galleryLayout.addWidget(self.scrollArea)
        # Add the right navigation button
        self.nextImageButton = QPushButton(">", self)
        self.nextImageButton.clicked.connect(self.nextImage)
        self.galleryLayout.addWidget(self.nextImageButton)

    def toggleImageGallery(self):
        if self.inImageGalleryMode:
            # Hide gallery and show live feed
            self.galleryWidget.hide()
            self.camera_label.show()
        else:
            # Hide live feed and show gallery
            self.camera_label.hide()
            self.galleryWidget.show()
            self.updateGallery()
        self.inImageGalleryMode = not self.inImageGalleryMode

    
    
    
    ### Websocket Client Console ###
    def start_websocket_client(self, uri):
        self.commandServer_thread = sendCommand(uri, 65432) # Keep the ports static for easier use
        self.videoServer = vidServer(6789)
        self.updateConsole = threading.Thread(target=self.log_to_console,args=(51000,)) # 51000 is the port
        self.updateConsole.daemon = True
        self.updateConsole.start()


    def send_message_to_server(self):
        message = self.userMessageInput.text()
        self.commandServer_thread.sendMsg(message)
        self.userMessageInput.clear()
    
    
    
    def log_to_console(self, port):
        self.receiveMessageThread = receiveMessage('', port)
        while(1):
            message = self.receiveMessageThread.getMessage()
            if message is not None:
                self.console.append(message)
            time.sleep(3)

    
    
    
    
    
    
    ###Star Finder Main button function###
    def find_star(self):
        star_hip_number = self.starInput.text()
        self.lookup_star(star_hip_number)
    
    
    ###Star Finder driver Function###
    def get_star_coordinates(self, hip_number):
        planets = load('de421.bsp')
        earth = planets['earth']
        star_data = self.stars.loc[hip_number]

        from skyfield.api import Star
        star = Star(ra_hours=star_data['ra_hours'], dec_degrees=star_data['dec_degrees'])

        observer = earth + Topos(latitude_degrees=34.0, longitude_degrees=-118.0)
        ts = load.timescale()
        t = ts.now()

        astrometric = observer.at(t).observe(star)
        alt, az, distance = astrometric.apparent().altaz()

        ra_dec_coordinates = f"RA: {star.ra.hours}, DEC: {star.dec.degrees}"
        alt_az_coordinates = f"Altitude: {alt.degrees:.2f}, Azimuth: {az.degrees:.2f}"
        return ra_dec_coordinates, alt_az_coordinates


    
    ###Star Finder Database Function###
    def lookup_star(self, hip_number, star_name=None):
        try:
            hip_number = int(hip_number)
            ra_dec_coordinates, alt_az_coordinates = self.get_star_coordinates(hip_number)
            star_name = star_name if star_name else f"Star HIP {hip_number}"
            self.starNameLabel.setText(f"Star: {star_name}")
            self.resultLabel.setText(f"RA/DEC: {ra_dec_coordinates}")
            self.altAzLabel.setText(f"Alt/Az: {alt_az_coordinates}")
            # asyncio.run_coroutine_threadsafe(self.websocket_thread.send_message(f"{star_name} Coordinates: {alt_az_coordinates}"), self.websocket_thread.loop)
        except ValueError:
            self.resultLabel.setText("Invalid HIP number")
        except KeyError:
            self.resultLabel.setText("Star not found in catalog")

    ###Load HIP for Menu stars tool###
    def load_star_by_hip(self, hip_number, constellation_name):
        self.starInput.setText(str(hip_number))
        self.lookup_star(hip_number, constellation_name)


        planets = load('de421.bsp')
        earth = planets['earth']
        star_data = self.stars.loc[hip_number]

        from skyfield.api import Star
        star = Star(ra_hours=star_data['ra_hours'], dec_degrees=star_data['dec_degrees'])

        observer = earth + Topos(latitude_degrees=34.0, longitude_degrees=-118.0)
        ts = load.timescale()
        t = ts.now()

        astrometric = observer.at(t).observe(star)
        alt, az, distance = astrometric.apparent().altaz()

        ra_dec_coordinates = f"RA: {star.ra.hours}, DEC: {star.dec.degrees}"
        alt_az_coordinates = f"Altitude: {alt.degrees:.2f}, Azimuth: {az.degrees:.2f}"
        return ra_dec_coordinates, alt_az_coordinates

###Hipparcos Star Catalog###
def load_star_catalog():
    try:
        with load.open(hipparcos.URL) as f:
            stars = hipparcos.load_dataframe(f)
        return stars
    except Exception as e:
        print(f"Failed to load star catalog: {e}")
        return None

if __name__ == '__main__':
    app = QApplication([])

    stars = load_star_catalog()
    if stars is not None:
        ex = StarFinderGUI(stars)
        ex.show()
        sys.exit(app.exec())
    else:
        print("Unable to load the star catalog. Please check your internet connection and try again.")
