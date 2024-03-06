import os
import shutil

from makerelease import MakeRelease


def test_make_release():
    test_videos_folder = "tests/videos"
    video_filenames = [f for f in os.listdir(test_videos_folder) if f.endswith(("avi", "mkv", "mp4"))]

    for video_filename in video_filenames:
        print(f"Testing {video_filename}...")
        basename = os.path.splitext(video_filename)[0]
        dir_path = os.path.join(test_videos_folder, basename + "_files")
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)

        release_maker = MakeRelease(
            crew="TestCrew",
            rename=False,
            type="movie",
            path=os.path.join(test_videos_folder, video_filename),
            id="693134",  # TheMovieDB ID is already specified to avoid user interaction
        )

        release_maker.make_release()
