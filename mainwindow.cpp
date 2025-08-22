#include "mainwindow.h"
#include "./ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    this->start_time = 0;
    this->end_time = -1;
    this->video_bitrate = -1;
    this->audio_bitrate = 128;
    this->total_bitrate = -1;
    this->estimated_size = -1;

    this->fileName = "";

    connect(ui->getBitrate, &QPushButton::released, this, &MainWindow::handleGetBitrate);
    connect(ui->getEstimatedSize, &QPushButton::released, this, &MainWindow::handleGetEstimatedSize);

    connect(ui->startTime, &QLineEdit::textChanged, this, &MainWindow::startTimeChanged);
    connect(ui->endTime, &QLineEdit::textChanged, this, &MainWindow::endTimeChanged);
    connect(ui->videoBitrate, &QLineEdit::textChanged, this, &MainWindow::videoBitrateChanged);
    connect(ui->audioBitrate, &QLineEdit::textChanged, this, &MainWindow::audioBitrateChanged);
    connect(ui->totalBitrate, &QLineEdit::textChanged, this, &MainWindow::totalBitrateChanged);
    connect(ui->estimatedSize, &QLineEdit::textChanged, this, &MainWindow::estimatedSizeChanged);

    connect(ui->selectVideo, &QPushButton::released, this, &MainWindow::handleSelectVideo);
    connect(ui->compressVideo, &QPushButton::released, this, &MainWindow::handleCompressVideo);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::startTimeChanged() {
    if (ui->startTime->text().isEmpty()) {
        this->start_time = -1;
        return;
    }
    bool ok;
    int start_time = ui->startTime->text().toInt(&ok, 10);
    if (!ok) {
        if (this->start_time == -1) {
            ui->startTime->clear();
        } else {
            ui->startTime->setText(QString::number(this->start_time));
        }
    } else {
        this->start_time = start_time;
    }
}

void MainWindow::endTimeChanged() {
    if (ui->endTime->text().isEmpty()) {
        this->end_time = -1;
        return;
    }
    bool ok;
    int end_time = ui->endTime->text().toInt(&ok, 10);
    if (!ok) {
        if (this->end_time == -1) {
            ui->endTime->clear();
        } else {
            ui->endTime->setText(QString::number(this->end_time));
        }
    } else {
        this->end_time = end_time;
    }
}

void MainWindow::videoBitrateChanged() {
    if (ui->videoBitrate->text().isEmpty()) {
        this->video_bitrate = -1;
        return;
    }
    bool ok;
    int video_bitrate = ui->videoBitrate->text().toInt(&ok, 10);
    if (!ok) {
        if (this->video_bitrate == -1) {
            ui->videoBitrate->clear();
        } else {
            ui->videoBitrate->setText(QString::number(this->video_bitrate));
        }
    } else {
        this->video_bitrate = video_bitrate;
        if (this->audio_bitrate != -1) {
            this->total_bitrate = this->video_bitrate + this->audio_bitrate;
            ui->totalBitrate->setText(QString::number(this->total_bitrate));
        }
    }
}

void MainWindow::audioBitrateChanged() {
    if (ui->audioBitrate->text().isEmpty()) {
        this->audio_bitrate = -1;
        return;
    }
    bool ok;
    int audio_bitrate = ui->audioBitrate->text().toInt(&ok, 10);
    if (!ok) {
        if (this->audio_bitrate == -1) {
            ui->audioBitrate->clear();
        } else {
            ui->audioBitrate->setText(QString::number(this->audio_bitrate));
        }
    } else {
        this->audio_bitrate = audio_bitrate;
        if (this->video_bitrate != -1) {
            this->total_bitrate = this->video_bitrate + this->audio_bitrate;
            ui->totalBitrate->setText(QString::number(this->total_bitrate));
        }
    }
}

void MainWindow::totalBitrateChanged() {
    if (ui->totalBitrate->text().isEmpty()) {
        this->total_bitrate = -1;
        return;
    }
    bool ok;
    int total_bitrate = ui->totalBitrate->text().toInt(&ok, 10);
    if (!ok) {
        if (this->total_bitrate == -1) {
            ui->totalBitrate->clear();
        } else {
            ui->totalBitrate->setText(QString::number(this->total_bitrate));
        }
    } else {
        this->total_bitrate = total_bitrate;
    }
}

void MainWindow::estimatedSizeChanged() {
    if (ui->estimatedSize->text().isEmpty()) {
        this->estimated_size = -1;
        return;
    }
    bool ok;
    int estimated_size = ui->estimatedSize->text().toInt(&ok, 10);
    if (!ok) {
        if (this->estimated_size == -1) {
            ui->estimatedSize->clear();
        } else {
            ui->estimatedSize->setText(QString::number(this->estimated_size));
        }
    } else {
        this->estimated_size = estimated_size;
    }
}

// assumes 2 kbps of overhead
void MainWindow::handleGetBitrate() {
    if (this->audio_bitrate == -1 || this->estimated_size == -1 || this->start_time == -1 || this->end_time == -1) {
        return;
    }

    long time = this->end_time - this->start_time;

    long bitrate = 8 * this->estimated_size / time;

    if (this->audio_bitrate + 2 >= bitrate) {
        return;
    }

    this->total_bitrate = bitrate - 2;
    ui->totalBitrate->setText(QString::number(this->total_bitrate));

    this->video_bitrate = this->total_bitrate - this->audio_bitrate;
    ui->videoBitrate->setText(QString::number(this->video_bitrate));
}

// assumes 2 kbps of overhead
void MainWindow::handleGetEstimatedSize() {
    if (this->total_bitrate == -1 || this->start_time == -1 || this->end_time == -1) {
        return;
    }

    long time = this->end_time - this->start_time;

    long bitrate = total_bitrate + 2;

    this->estimated_size = bitrate * time / 8;
    ui->estimatedSize->setText(QString::number(this->estimated_size));
}

void MainWindow::handleSelectVideo() {
    QString fileName = QFileDialog::getOpenFileName(this, tr("Open File"),
                                                    "/home",
                                                    tr("Videos"));
    this->fileName = fileName;
}

void MainWindow::handleCompressVideo() {
    if (this->start_time == -1 || this->end_time == -1 || this->video_bitrate == -1 || this->audio_bitrate == -1) {
        qInfo() << "Arguments not set";
        return;
    }
    QProcess process;
    // QStringList arguments = QStringList() << "-i" << this->fileName << "-b:v" << QString::number(this->video_bitrate) + "k" << "-b:a" << "128k" << "output.mp4";
    // qInfo() << "ffmpeg" << arguments;
    // process.start("ffmpeg", arguments);


    process.setProgram("ffmpeg");
    process.setArguments(QStringList() << "-i" << this->fileName << "-r" << "30" << "-b" << QString::number(this->video_bitrate) + "k" << "-b:a" << "128k" << "output.mp4");
    qInfo() << process.program() << process.arguments();
    process.start();
    if (!process.waitForFinished(-1)) {
        qDebug() << "Stopped" << process.errorString();
        return;
    }
    if (process.exitCode() != 0) {
        qDebug() << " Error " << process.exitCode() << process.readAllStandardError();
    }
    qInfo() << "done";
    qDebug() << process.readAll();
}
