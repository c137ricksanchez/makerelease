import subprocess


def get_report(FILENAME):
    report = subprocess.run(['mediainfo', FILENAME], capture_output=True)
    return report.stdout.decode("utf-8")


def extract_screenshots(FILENAME):

    timecodes = ['00:05:00',
                 '00:10:00',
                 '00:15:00',
                 '00:20:00',
                 '00:25:00',
                 '00:30:00',
                 '00:35:00',
                 '00:40:00',
                 '00:45:00',
                 '00:50:00',
                 '00:55:00']
    for time in timecodes:
        name = FILENAME.split('.')[-2] + '_SCREENSHOT_' + time.replace(':', '-') + '.jpg'
        subprocess.run(['ffmpeg', '-ss', time, '-i', FILENAME, '-vframes', '1', '-q:v', '2', name])
