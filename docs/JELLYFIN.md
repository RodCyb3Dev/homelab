# Jellyfin Complete Guide

Complete guide for Jellyfin setup, hardware acceleration, and performance optimization.

---

## 📋 Overview

Jellyfin is your self-hosted media server for movies and TV shows. This guide covers:
- Hardware acceleration setup (even on virtualized servers)
- Performance optimization
- Transcoding configuration
- Troubleshooting

**Current Server Configuration:**
- **Server**: CPX21 (3 vCPU, 4GB RAM)
- **GPU**: Virtio GPU (virtualized)
- **Device**: `/dev/dri` mounted with `card0` and `renderD128`
- **Groups**: `video` (GID 44), `render` (GID 993)

---

## 🚀 Hardware Acceleration Setup

### Docker Compose Configuration

The `/dev/dri` device is mounted in the Jellyfin container:

```yaml
devices:
  - /dev/dri:/dev/dri
```

### Jellyfin Settings

Even though the Virtio GPU may not support full hardware acceleration, it's worth trying VA-API:

1. **Navigate to**: Dashboard → Playback → Transcoding

2. **Hardware Acceleration Settings**:
   - **Hardware acceleration**: `Video Acceleration API (VA-API)`
   - **VA-API device**: `/dev/dri/renderD128`
   - **Enable hardware encoding**: `On` (if supported)
   - **Enable hardware decoding**: `On` (if supported)

3. **Test Hardware Acceleration**:
   - Try playing a video that requires transcoding
   - Check Dashboard → Dashboard → Active Devices
   - Look for "Hardware" indicator in transcoding status

### Verifying Device Access

Check if the device is accessible in the container:

```bash
docker exec jellyfin ls -la /dev/dri/
```

Should show:
```
card0
renderD128
```

### Testing VA-API Support

Test if VA-API works with the Virtio GPU:

```bash
docker exec jellyfin /usr/lib/jellyfin-ffmpeg/ffmpeg -hwaccels
```

This will list available hardware acceleration methods.

### Limitations

**Virtio GPU Limitations:**
- Virtio GPU is a virtualized GPU that may not support hardware acceleration
- Most virtualized GPUs don't have hardware encoders/decoders
- Software transcoding will likely still be used as fallback

**If Hardware Acceleration Doesn't Work:**
- The system will automatically fall back to software transcoding
- The tmpfs mount for transcoding cache will still provide performance benefits
- Optimized encoder presets will help with software transcoding

---

## ⚡ Performance Optimization

### 1. Transcoding Cache in RAM (tmpfs)

Transcoding temporary files are stored in RAM instead of disk, providing:
- **10-100x faster I/O** compared to network storage
- Reduced latency during transcoding
- Better performance for multiple concurrent streams

**Configuration:**
```yaml
tmpfs:
  - /config/data/transcodes:size=2G  # 2GB RAM for transcoding cache
```

### 2. Software Transcoding Settings

Since hardware acceleration is not available on virtualized servers, we optimize software transcoding:

**Key Settings:**
- **Encoder Preset**: `veryfast` (faster encoding, lower CPU usage)
- **Hardware Acceleration**: Disabled (not available on Virtio GPU)
- **Throttling**: Enabled (prevents CPU overload)
- **Segment Deletion**: Enabled (saves disk space)

### 3. Jellyfin Dashboard Settings

After deploying, configure these settings in Jellyfin Web UI:

1. **Navigate to**: Dashboard → Playback → Transcoding

2. **Recommended Settings:**
   - **Hardware acceleration**: `None` (or `VideoToolbox` if available)
   - **Enable hardware encoding**: `Off`
   - **Enable hardware decoding**: `Off`
   - **Transcoding temporary path**: `/config/data/transcodes`
   - **Encoder preset**: `Very Fast`
   - **Enable throttling**: `On`
   - **Throttle delay**: `60 seconds`
   - **Enable segment deletion**: `On`
   - **Segment keep time**: `5 minutes`

3. **Playback Settings:**
   - **Enable video encoding**: `On`
   - **Allow HEVC encoding**: `On` (better compression)
   - **Allow AV1 encoding**: `Off` (not supported on virtualized servers)
   - **Enable subtitle extraction**: `On`

### 4. Additional Performance Tips

#### Direct Play When Possible

To avoid transcoding entirely:
- Use clients that support your media formats (e.g., MP4/H.264)
- Pre-encode media to compatible formats
- Use Jellyfin clients that support direct play

#### Reduce Transcoding Load

1. **Pre-transcode media** to common formats:
   - Container: MP4
   - Video: H.264 (AVC)
   - Audio: AAC
   - Resolution: 1080p or lower for mobile devices

2. **Limit concurrent transcodes**:
   - Set maximum concurrent transcodes in Dashboard → Playback
   - Recommended: 2-3 concurrent transcodes for CPX21 server

3. **Use lower bitrate profiles**:
   - Configure quality profiles in Dashboard → Playback → Quality
   - Lower bitrates = faster transcoding

#### Monitor Performance

1. **Check transcoding status**:
   - Dashboard → Dashboard → Active Devices
   - Look for "Transcoding" indicator

2. **Monitor CPU usage**:
   - Use `htop` or `docker stats jellyfin`
   - CPU should stay below 80% during transcoding

3. **Check transcoding cache**:
   - `docker exec jellyfin df -h /config/data/transcodes`
   - Should show tmpfs mount with available space

---

## 🐛 Troubleshooting

### Slow Playback Still Occurs

1. **Check if transcoding is happening**:
   - Dashboard → Dashboard → Active Devices
   - If transcoding, check CPU usage

2. **Verify tmpfs mount**:
   ```bash
   docker exec jellyfin df -h /config/data/transcodes
   ```
   Should show tmpfs, not a regular filesystem

3. **Check network speed**:
   - Storage Box is network-mounted, may be slow
   - Consider pre-transcoding media to reduce load

### High CPU Usage

1. **Reduce concurrent transcodes**:
   - Dashboard → Playback → Transcoding
   - Set "Maximum concurrent transcodes" to 2

2. **Use faster encoder preset**:
   - Change from "veryfast" to "ultrafast" (lower quality, faster)

3. **Enable throttling**:
   - Already enabled, but verify in settings

### Out of Memory Errors

1. **Reduce tmpfs size**:
   - Edit `docker-compose.arr-stack.yml`
   - Change `size=2G` to `size=1G`

2. **Limit concurrent transcodes**:
   - Reduce to 1-2 concurrent transcodes

### Hardware Acceleration Not Working

1. **Verify device access**:
   ```bash
   docker exec jellyfin ls -la /dev/dri/
   ```

2. **Check VA-API support**:
   ```bash
   docker exec jellyfin /usr/lib/jellyfin-ffmpeg/ffmpeg -hwaccels
   ```

3. **Fall back to software transcoding**:
   - Set hardware acceleration to `None`
   - Use optimized software transcoding settings (see above)

---

## 📚 References

- [Jellyfin Hardware Acceleration Docs](https://jellyfin.org/docs/general/post-install/transcoding/hardware-acceleration/)
- [VA-API on Linux](https://jellyfin.org/docs/general/post-install/transcoding/hardware-acceleration/intel#linux-setups)
- [Maximizing Jellyfin Performance](https://www.oreateai.com/blog/maximizing-jellyfin-performance-a-guide-to-hardware-acceleration-and-tuning/b170e22857273f989c3299afd1129e5c)

---

## ✅ Quick Setup Checklist

- [ ] `/dev/dri` device mounted in Docker Compose
- [ ] tmpfs transcoding cache configured (2GB)
- [ ] Jellyfin dashboard settings configured
- [ ] Hardware acceleration tested (if available)
- [ ] Software transcoding optimized (if hardware not available)
- [ ] Concurrent transcodes limited (2-3 for CPX21)
- [ ] Performance monitoring set up

---

**Your Jellyfin server is now optimized for performance!** 🎬
