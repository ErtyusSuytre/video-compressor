#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QFileDialog>
#include <QDebug>
#include <QProcess>

QT_BEGIN_NAMESPACE
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private:
    Ui::MainWindow *ui;
    long start_time; // seconds
    long end_time; // seconds
    long video_bitrate; // kbps
    long audio_bitrate; // kbps
    long total_bitrate; // kbps
    long estimated_size; // MB

    QString fileName;

    void setVideoBitrate(int bitrate);
    void setAudioBitrate(int bitrate);
    void setTotalBitrate(int bitrate);

private slots:
    void startTimeChanged();
    void endTimeChanged();
    void videoBitrateChanged();
    void audioBitrateChanged();
    void totalBitrateChanged();
    void estimatedSizeChanged();

    void handleGetBitrate();
    void handleGetEstimatedSize();

    void handleSelectVideo();
    void handleCompressVideo();
};
#endif // MAINWINDOW_H
