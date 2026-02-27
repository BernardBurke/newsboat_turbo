#!/usr/bin/env python3
import sys
import json
import uuid
import shutil
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QFormLayout, 
                             QPushButton, QLabel, QLineEdit, QTextEdit, 
                             QFileDialog, QDateEdit, QMessageBox)
from PyQt5.QtCore import QDate

class YodcastIngestor(QWidget):
    def __init__(self):
        super().__init__()
        self.audio_path = ""
        self.cover_path = ""
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Manual Yodcast Ingestor')
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Audio File Picker
        self.btn_audio = QPushButton('Select Audio File')
        self.btn_audio.clicked.connect(self.select_audio)
        self.lbl_audio = QLabel('No file selected')
        form_layout.addRow(self.btn_audio, self.lbl_audio)

        # Cover Art Picker
        self.btn_cover = QPushButton('Select Cover Art (Optional)')
        self.btn_cover.clicked.connect(self.select_cover)
        self.lbl_cover = QLabel('No file selected')
        form_layout.addRow(self.btn_cover, self.lbl_cover)

        # Text Inputs
        self.input_podcast = QLineEdit()
        form_layout.addRow('Podcast / Channel Name:', self.input_podcast)

        self.input_episode = QLineEdit()
        form_layout.addRow('Episode Title:', self.input_episode)

        self.input_desc = QTextEdit()
        form_layout.addRow('Description:', self.input_desc)

        # Date Picker (Defaults to today)
        self.input_date = QDateEdit()
        self.input_date.setCalendarPopup(True)
        self.input_date.setDate(QDate.currentDate())
        form_layout.addRow('Publish Date:', self.input_date)

        layout.addLayout(form_layout)

        # Submit Button
        self.btn_submit = QPushButton('Generate Yodcast Package')
        self.btn_submit.setStyleSheet("background-color: #2e8b57; color: white; font-weight: bold; padding: 10px;")
        self.btn_submit.clicked.connect(self.process_submission)
        layout.addWidget(self.btn_submit)

        self.setLayout(layout)

    def select_audio(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.m4a *.wav *.ogg)")
        if file:
            self.audio_path = file
            self.lbl_audio.setText(os.path.basename(file))

    def select_cover(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Cover Art", "", "Image Files (*.jpg *.jpeg *.png *.webp)")
        if file:
            self.cover_path = file
            self.lbl_cover.setText(os.path.basename(file))

    def process_submission(self):
        if not self.audio_path or not self.input_podcast.text() or not self.input_episode.text():
            QMessageBox.warning(self, "Error", "Audio file, Podcast Name, and Episode Title are required!")
            return

        # Generate a unique ID (e.g., manual_8f4b2a)
        unique_id = f"manual_{uuid.uuid4().hex[:6]}"
        ext = self.audio_path.split('.')[-1]
        
        # Format date for yt-dlp (YYYYMMDD)
        date_str = self.input_date.date().toString("yyyyMMdd")

        # Build the mock yt-dlp dictionary
        mock_json = {
            "id": unique_id,
            "title": self.input_episode.text(),
            "uploader": self.input_podcast.text(),
            "channel": self.input_podcast.text(),
            "description": self.input_desc.toPlainText(),
            "upload_date": date_str,
            "ext": ext,
            "thumbnail": self.cover_path if self.cover_path else ""
        }

        # For testing, we just drop the files in the current directory
        # Later, we can point this to the SSHFS drop folder or Staging dir
        output_json_path = f"{unique_id}.info.json"
        output_audio_path = f"{unique_id}.{ext}"

        # 1. Write the JSON
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(mock_json, f, indent=4)

        # 2. Copy the audio file to match the ID
        shutil.copy2(self.audio_path, output_audio_path)

        QMessageBox.information(self, "Success", f"Generated {output_json_path}\nand {output_audio_path}")
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YodcastIngestor()
    ex.show()
    sys.exit(app.exec_())