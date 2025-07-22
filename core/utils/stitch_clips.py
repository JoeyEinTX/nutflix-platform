import subprocess
import logging
import os

def stitch_video_audio(video_path: str, audio_path: str, output_path: str, delete_originals: bool = False) -> bool:
    """
    Merge video and audio into a single output file using ffmpeg.
    Video is copied as-is, audio is encoded to AAC.
    Optionally deletes original files after success.
    Returns True if merge is successful, False otherwise.
    """
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        output_path
    ]
    try:
        logging.info(f"[Stitch] Running ffmpeg: {' '.join(cmd)}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logging.info(f"[Stitch] ffmpeg output: {result.stdout.decode(errors='ignore')}")
        if delete_originals:
            try:
                os.remove(video_path)
                os.remove(audio_path)
                logging.info(f"[Stitch] Deleted originals: {video_path}, {audio_path}")
            except Exception as e:
                logging.warning(f"[Stitch] Failed to delete originals: {e}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"[Stitch] ffmpeg failed: {e.stderr.decode(errors='ignore')}")
        return False
    except Exception as e:
        logging.error(f"[Stitch] Unexpected error: {e}")
        return False
