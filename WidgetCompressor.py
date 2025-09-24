from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QFileDialog, QRadioButton
from PySide6.QtCore import QThreadPool, QProcess, QStringDecoder
from FieldWidget import FieldWidget
import ffmpeg
from Worker import Worker
import logging

class WidgetCompressor(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Video Compressor")
        
        # Variables
        self.video_bitrate: Optional[int] = None
        self.audio_bitrate: Optional[int] = None
        self.total_bitrate: Optional[int] = None
        self.actual_total_bitrate: Optional[int] = None
        self.overhead: Optional[int] = None
        self.duration: Optional[int] = None
        self.framerate: Optional[int] = None
        self.file_info: Optional[dict] = None
        self.estimated_size: Optional[int] = None
        
        # Buttons
        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self.handle_import)
        self.compress_button = QPushButton("Compress")
        self.compress_button.clicked.connect(self.handle_compress)
        
        # Number Fields
        self.video_bitrate_field = FieldWidget("Video Bitrate", "kbps")
        self.video_bitrate_field.field.textEdited.connect(self.video_bitrate_changed)
        self.audio_bitrate_field = FieldWidget("Audio Bitrate", "kbps")
        self.audio_bitrate_field.field.textEdited.connect(self.audio_bitrate_changed)
        self.total_bitrate_field = FieldWidget("Total Bitrate", "kbps")
        self.total_bitrate_field.field.textEdited.connect(self.total_bitrate_changed)
        self.estimated_size_field = FieldWidget("Estimated Size", "bytes")
        self.estimated_size_field.field.textEdited.connect(self.estimated_size_changed)
        self.estimated_size_field.field.setPlaceholderText("Not Working Yet...")
        
        # Radio Buttons
        self.framerate_widget = QWidget()
        self.framerate_30 = QRadioButton("30fps")
        self.framerate_30.pressed.connect(self.handle_framerate_30)
        self.framerate_60 = QRadioButton("60fps")
        self.framerate_60.pressed.connect(self.handle_framerate_60)
        self.framerate_widget_layout = QHBoxLayout()
        self.framerate_widget_layout.addWidget(self.framerate_30)
        self.framerate_widget_layout.addWidget(self.framerate_60)
        self.framerate_widget.setLayout(self.framerate_widget_layout)
        
        # File Path
        self.current_file: Optional[str] = None
        self.file_path_field = QLabel("No File Selected")
        
        # Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.video_bitrate_field)
        self.layout.addWidget(self.audio_bitrate_field)
        self.layout.addWidget(self.total_bitrate_field)
        self.layout.addWidget(self.estimated_size_field)
        self.layout.addWidget(self.framerate_widget)
        self.layout.addWidget(self.file_path_field)
        self.layout.addWidget(self.import_button)
        self.layout.addWidget(self.compress_button)
        self.setLayout(self.layout)
        
        self.threadpool = QThreadPool()

    def video_bitrate_changed(self):
        if self.video_bitrate_field.field.text() == "" or self.audio_bitrate is None:
            return
        
        video_bitrate = int(self.video_bitrate_field.field.text())
        total_bitrate = video_bitrate + self.audio_bitrate
        actual_total_bitrate = total_bitrate + self.overhead
        
        if video_bitrate <= 0 or total_bitrate <= 0 or actual_total_bitrate <= 0:
            logging.info("Invalid bitrate")
            return
        
        self.total_bitrate_field.field.setText(str(total_bitrate))
        self.estimated_size_field.field.setText(str(int(actual_total_bitrate*self.duration/8)+1))
        
        self.video_bitrate = video_bitrate
        self.total_bitrate = total_bitrate
        self.actual_total_bitrate = actual_total_bitrate
        
    def audio_bitrate_changed(self):
        if self.audio_bitrate_field.field.text() == "" or self.video_bitrate is None:
            return
        
        audio_bitrate = int(self.audio_bitrate_field.field.text())
        total_bitrate = self.video_bitrate + audio_bitrate
        actual_total_bitrate = total_bitrate + self.overhead
        
        if audio_bitrate <= 0 or total_bitrate <= 0 or actual_total_bitrate <= 0:
            logging.info("Invalid bitrate")
            return
        
        self.total_bitrate_field.field.setText(str(total_bitrate))
        self.estimated_size_field.field.setText(str(int(actual_total_bitrate*self.duration/8)+1))
        
        self.audio_bitrate = audio_bitrate
        self.total_bitrate = total_bitrate
        self.actual_total_bitrate = actual_total_bitrate
    
    def total_bitrate_changed(self):
        if self.total_bitrate_field.field.text() == "" or self.video_bitrate is None or self.audio_bitrate is None:
            return
        
        total_bitrate = int(self.total_bitrate_field.field.text())
        video_bitrate = total_bitrate - self.audio_bitrate
        actual_total_bitrate = total_bitrate + self.overhead
        
        if total_bitrate <= 0 or video_bitrate <= 0 or actual_total_bitrate <= 0:
            logging.info("Invalid bitrate")
            return
        
        self.video_bitrate_field.field.setText(str(video_bitrate))
        self.estimated_size_field.field.setText(str(int(actual_total_bitrate*self.duration/8)+1))
        
        self.video_bitrate = video_bitrate
        self.total_bitrate = total_bitrate
        self.actual_total_bitrate = actual_total_bitrate
        
    def estimated_size_changed(self):
        if self.estimated_size_field.field.text() == "" or self.actual_total_bitrate is None:
            return
        
        estimated_size = int(self.estimated_size_field.field.text())
        actual_total_bitrate = int(estimated_size * 8 / self.duration)
        total_bitrate = actual_total_bitrate - self.overhead
        video_bitrate = total_bitrate - self.audio_bitrate
        
        # TODO: add audio bitrate calculation down to 128kbps
        
        if total_bitrate <= 0 or video_bitrate <= 0 or actual_total_bitrate <= 0:
            logging.info("Invalid bitrate")
            return
        
        self.video_bitrate_field.field.setText(str(video_bitrate))
        self.total_bitrate_field.field.setText(str(total_bitrate))
        
        self.actual_total_bitrate = actual_total_bitrate
        self.total_bitrate = total_bitrate
        self.video_bitrate = video_bitrate
        
    def handle_framerate_30(self):
        # self.video_bitrate *= 30 / self.framerate
        # self.video_bitrate_field.field.setText(str(self.video_bitrate))
        # self.total_bitrate = self.video_bitrate + self.audio_bitrate
        # self.total_bitrate_field.field.setText(str(self.total_bitrate))
        # self.actual_total_bitrate = self.total_bitrate + self.overhead
        # self.estimated_size_field.field.setText(str(int(self.actual_total_bitrate*self.duration/8)+1))
        
        self.framerate = 30
        
        
    def handle_framerate_60(self):
        # self.video_bitrate *= 60 / self.framerate
        # self.video_bitrate_field.field.setText(str(self.video_bitrate))
        # self.total_bitrate = self.video_bitrate + self.audio_bitrate
        # self.total_bitrate_field.field.setText(str(self.total_bitrate))
        # self.actual_total_bitrate = self.total_bitrate + self.overhead
        # self.estimated_size_field.field.setText(str(int(self.actual_total_bitrate*self.duration/8)+1))
        
        self.framerate = 60
    
    def handle_import(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Video Files (*.mp4, *.mov)")
        if dialog.exec():
            file_path = dialog.selectedFiles()[0]
            self.current_file = file_path
            self.file_path_field.setText(file_path)
            probe_worker = Worker(self.ffmpeg_probe)
            probe_worker.signals.finished.connect(self.handle_finished_probe)
            self.threadpool.start(probe_worker)
            
    def handle_compress(self):
        if self.current_file is None:
            logging.info("No file selected")
            return
        worker = Worker(self.ffmpeg_compress)
        worker.signals.finished.connect(self.handle_finished_compress)
        self.threadpool.start(worker)
    
    def handle_finished_probe(self):
        logging.info("Finished Probing")
        self.parse_file_info()
        logging.info("Finished Parsing")
        
    def handle_finished_compress(self):
        logging.info("Finished Compressing")
    
    # Only works with ffmpeg in PATH
    # def ffmpeg_compress(self):
    #     stream = ffmpeg.input(self.current_file)
    #     stream = ffmpeg.output(stream, self.current_file[:-4]+"_compressed"+self.current_file[-4:], video_bitrate=self.video_bitrate, audio_bitrate=self.audio_bitrate, r=self.framerate)
    #     ffmpeg.run(stream)
    
    def ffmpeg_compress(self):
        process = QProcess()
        process.setProgram("./lib/ffmpeg/bin/ffmpeg.exe")
        process.setArguments(["-i", self.current_file, "-b:v", str(self.video_bitrate), "-b:a", str(self.audio_bitrate), "-r", str(self.framerate), self.current_file[:-4]+"_compressed"+self.current_file[-4:]], "-y")
        process.start()
        if process.waitForFinished():
            logging.info("Compression Finished")
        else:
            logging.error("Compression Failed")

    def ffmpeg_probe(self):
        logging.info("Getting File Info...")
        try:
            self.file_info = ffmpeg.probe(self.current_file, cmd="./lib/ffmpeg/bin/ffprobe.exe")
        except Exception as e:
            logging.error(e)
            return
    
    # TODO: Parse ffprobe output with regex
    # def ffmpeg_probe(self):
    #     process = QProcess()
    #     process.setProgram("./lib/ffmpeg/bin/ffprobe.exe")
    #     process.setArguments([self.current_file])
    #     process.start()
    #     if process.waitForFinished():
    #         logging.info("File Info Fetched")
    #         print(process.readAllStandardOutput())
        
    def parse_file_info(self):
        logging.info("Parsing File Info...")
        try:
            self.duration = float(self.file_info["format"]["duration"])
            self.video_bitrate = int(self.file_info["streams"][0]["bit_rate"])
            self.video_bitrate_field.field.setText(str(self.video_bitrate))
            if len(self.file_info["streams"]) < 2:
                logging.info("No Audio Stream Found")
                self.audio_bitrate = 0
            else:
                self.audio_bitrate = int(self.file_info["streams"][1]["bit_rate"])
            self.audio_bitrate_field.field.setText(str(self.audio_bitrate))
            self.total_bitrate = self.video_bitrate + self.audio_bitrate
            self.total_bitrate_field.field.setText(str(self.total_bitrate))
            self.actual_total_bitrate = int(self.file_info["format"]["bit_rate"])
            self.estimated_size_field.field.setText(str(int(self.actual_total_bitrate*self.duration/8)+1))
            self.overhead = self.actual_total_bitrate - self.total_bitrate
            framerate, dur = self.file_info["streams"][0]["r_frame_rate"].split("/")
            if dur != "1":
                logging.warning("Non Standard Framerate: "+framerate+"/"+dur)
            self.framerate = int(float(framerate)/float(dur))
            if self.framerate == 30:
                self.framerate_30.setChecked(True)
            elif self.framerate == 60:
                self.framerate_60.setChecked(True)
        except Exception as e:
            logging.error(e)
            return
        # import json
        # print(json.dumps(self.file_info, indent=4))