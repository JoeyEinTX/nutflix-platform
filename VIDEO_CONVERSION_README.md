# Nutflix Video Auto-Conversion Setup

## Overview
This system automatically converts video files to H.264 format for optimal web browser compatibility. The conversion service runs in the background and monitors the `/recordings/` directory for new videos.

## Architecture
- **Auto-Converter**: `auto_convert_videos.py` monitors `/recordings/` and converts videos to H.264
- **Flask Backend**: Automatically serves H.264 versions when available
- **React Frontend**: Uses standard `/api/clips/` endpoint for all videos

## Quick Start

### 1. Install Dependencies
```bash
# Install Python dependencies
pip install watchdog

# Ensure FFmpeg is available
ffmpeg -version
```

### 2. Start Both Services
```bash
# Terminal 1: Start the auto-conversion service
python3 auto_convert_videos.py &

# Terminal 2: Start the Flask backend
python3 dashboard/app_with_react.py
```

### 3. Alternative: Run Both as Background Services
```bash
# Start both services in background
nohup python3 auto_convert_videos.py > convert.log 2>&1 &
nohup python3 dashboard/app_with_react.py > flask.log 2>&1 &

# Check if both are running
ps aux | grep python
```

## How It Works

### Auto-Conversion Process
1. **Monitor**: Watches `/recordings/` for new `.mp4` files
2. **Detect**: Uses `ffprobe` to check if video is already H.264
3. **Convert**: If not H.264, converts using FFmpeg with web-optimized settings:
   - H.264 video codec (`libx264`)
   - AAC audio codec
   - GOP size 30 for web streaming
   - Fast start enabled (`+faststart`)
   - Output: `original_filename_h264.mp4`
4. **Skip**: Avoids re-converting files that are already H.264

### Flask Video Serving
The `/api/clips/<path>` endpoint now intelligently serves videos:

1. **Check for H.264 version**: If `video.mp4` exists, look for `video_h264.mp4`
2. **Serve H.264 first**: If H.264 version exists, serve that instead
3. **Fallback**: If no H.264 version, serve original file
4. **Headers**: Proper CORS, caching, and streaming headers for browser compatibility

### React Frontend
- Uses single endpoint: `http://10.0.0.82:8000/api/clips/<path>`
- Automatically gets best available video format
- No changes needed when H.264 versions become available

## File Structure
```
/recordings/
├── 20250214_211522_nt_squirrel.mp4      # Original MPEG-4 file
├── 20250214_211522_nt_squirrel_h264.mp4 # Auto-converted H.264 version
└── auto_convert.log                      # Conversion service logs
```

## Configuration

### FFmpeg Conversion Settings
```python
# In auto_convert_videos.py
FFMPEG_TIMEOUT = 300      # 5 minutes max per conversion
RETRY_DELAY = 30          # Wait 30 seconds before retry
```

### Video Quality Settings
```bash
# FFmpeg command used for conversion
ffmpeg -i input.mp4 \
  -c:v libx264 \          # H.264 codec
  -preset medium \        # Balanced speed/quality
  -crf 23 \              # Good quality (lower = better)
  -g 30 \                # GOP size for web streaming
  -c:a aac \             # AAC audio
  -b:a 128k \            # Audio bitrate
  -movflags +faststart \ # Web optimization
  -pix_fmt yuv420p \     # Browser compatibility
  output_h264.mp4
```

## Monitoring

### Check Conversion Service Status
```bash
# View conversion logs
tail -f auto_convert.log

# Check if service is running
ps aux | grep auto_convert_videos

# View recent conversions
ls -la recordings/*_h264.mp4
```

### Flask Backend Logs
```bash
# Monitor Flask video serving
tail -f flask.log

# Check which videos are being served
grep "Serving" flask.log
```

## Troubleshooting

### Common Issues

1. **FFmpeg Not Found**
   ```bash
   # Install FFmpeg
   sudo apt install ffmpeg  # Ubuntu/Debian
   brew install ffmpeg      # macOS
   ```

2. **Permission Issues**
   ```bash
   # Ensure recordings directory is writable
   chmod 755 recordings/
   ```

3. **Conversion Failures**
   ```bash
   # Check conversion logs
   grep "❌" auto_convert.log
   
   # Manually test conversion
   ffmpeg -i recordings/test.mp4 -c:v libx264 test_h264.mp4
   ```

4. **Video Still Not Playing**
   - Check browser console for errors
   - Verify H.264 file was created: `ls recordings/*_h264.mp4`
   - Test direct URL: `http://10.0.0.82:8000/api/clips/recordings/file_h264.mp4`

### Performance Tips

1. **Batch Convert Existing Files**
   ```python
   # Run conversion service once to process all existing files
   python3 auto_convert_videos.py
   # Will scan and convert all non-H.264 files in /recordings/
   ```

2. **Monitor System Resources**
   ```bash
   # Watch CPU/memory during conversion
   htop
   
   # Limit concurrent conversions if needed
   # (modify threading in auto_convert_videos.py)
   ```

## Production Deployment

### Systemd Service (Linux)
```ini
# /etc/systemd/system/nutflix-convert.service
[Unit]
Description=Nutflix Video Auto-Converter
After=network.target

[Service]
Type=simple
User=nutflix
WorkingDirectory=/path/to/Nutflix-platform
ExecStart=/usr/bin/python3 auto_convert_videos.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable nutflix-convert.service
sudo systemctl start nutflix-convert.service
sudo systemctl status nutflix-convert.service
```

### Docker Deployment
```dockerfile
# Add to existing Dockerfile
RUN apt-get update && apt-get install -y ffmpeg
COPY auto_convert_videos.py .
RUN pip install watchdog

# In docker-compose.yml
services:
  nutflix-converter:
    build: .
    command: python3 auto_convert_videos.py
    volumes:
      - ./recordings:/app/recordings
  
  nutflix-backend:
    build: .
    command: python3 dashboard/app_with_react.py
    ports:
      - "8000:8000"
```

## Benefits

1. **No On-the-Fly Conversion**: Pre-converted H.264 files serve instantly
2. **Browser Compatibility**: H.264 + AAC works in all modern browsers
3. **Automatic**: New videos are converted without manual intervention
4. **Fallback**: Original files still work if conversion hasn't completed
5. **Performance**: No conversion delays during video playback
6. **Quality**: Optimized encoding settings for web streaming

## Next Steps

1. **Test the setup**: Upload a new video file and verify it gets converted
2. **Monitor performance**: Check conversion times and system resources
3. **Optimize settings**: Adjust FFmpeg parameters based on your needs
4. **Scale**: Add multiple conversion workers if needed for high volume
