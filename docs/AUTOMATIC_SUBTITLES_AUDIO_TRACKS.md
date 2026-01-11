# Automatic Subtitles and Audio Tracks Guide

This guide explains how to automatically download subtitles and handle multiple audio tracks for movies and TV shows in your Jellyfin setup.

---

## 🎯 Overview

Your homelab already includes **Bazarr**, which automatically downloads subtitles. This guide covers:
1. **Bazarr Configuration** - Automatic subtitle downloading
2. **Jellyfin Subtitle Settings** - Built-in subtitle management
3. **Multiple Audio Tracks** - Getting media with multiple languages
4. **Sonarr/Radarr Configuration** - Preferring multi-audio releases

---

## 📥 Method 1: Bazarr (Automatic Subtitle Downloading)

Bazarr is already running in your stack and can automatically download subtitles for all your media.

### Step 1: Access Bazarr

1. **Access Bazarr Web UI:**
   - URL: `https://anduin.kooka-lake.ts.net:6767`
   - Login with default credentials (usually no password on first run)

### Step 2: Configure Sonarr/Radarr Integration

1. **Go to Settings → General → Sonarr:**
   - **Host:** `http://gluetun:8989` (internal Docker network)
   - **API Key:** Enter your Sonarr API key (from `.env` or Sonarr settings)
   - **Base URL:** Leave empty (unless Sonarr uses a base path)
   - Click **Test** to verify connection

2. **Go to Settings → General → Radarr:**
   - **Host:** `http://gluetun:7878` (internal Docker network)
   - **API Key:** Enter your Radarr API key (from `.env` or Radarr settings)
   - **Base URL:** Leave empty (unless Radarr uses a base path)
   - Click **Test** to verify connection

### Step 3: Configure Subtitle Providers

1. **Go to Settings → Subtitles → Providers:**
   - Enable subtitle providers:
     - ✅ **OpenSubtitles** (free, requires account)
     - ✅ **Subscene** (free)
     - ✅ **Podnapisi** (free)
     - ✅ **Addic7ed** (free, requires account)
     - ✅ **LegendasTV** (free, requires account)
     - ✅ **Titulky** (free, requires account)

2. **Configure OpenSubtitles (Recommended):**
   - Visit: https://www.opensubtitles.org/en/account/register
   - Create a free account
   - Go to Bazarr → Settings → Subtitles → Providers → OpenSubtitles
   - Enter your **Username** and **Password**
   - Click **Test** to verify

### Step 4: Configure Languages

1. **Go to Settings → Subtitles → Languages:**
   - **Languages to download:** Select your preferred languages
     - Example: `English`, `Spanish`, `French`, `German`, `Arabic`, etc.
   - **Minimum Score:** `0` (downloads best available match)
   - **Upgrade previously downloaded subtitles:** ✅ Enabled (updates if better subtitles found)

### Step 5: Configure Automatic Downloading

1. **Go to Settings → Subtitles → Subtitles:**
   - ✅ **Automatic Subtitles Downloading:** Enabled
   - **Download Subtitles for:** 
     - ✅ Movies
     - ✅ Episodes
   - **Download Subtitles for:** 
     - ✅ Manual Search (when you add new media)
     - ✅ Scheduled Search (periodic checks for missing subtitles)
   - **Scheduled Task:** Set interval (e.g., every 6 hours)

2. **Go to Settings → Subtitles → Subtitles → Scheduled Tasks:**
   - ✅ **Download Subtitles:** Enabled
   - **Interval:** `6` hours (or your preference)
   - **Retry Failed Downloads:** ✅ Enabled

### Step 6: Configure Media Paths

1. **Go to Settings → General → Paths:**
   - **Movies Path:** `/media/movies` (matches your Radarr path)
   - **TV Shows Path:** `/media/tv-shows` (matches your Sonarr path)
   - These should match your Sonarr/Radarr root folders

---

## 🎬 Method 2: Jellyfin Built-in Subtitle Features

Jellyfin has built-in subtitle management features.

### Configure Subtitle Downloads in Jellyfin

1. **Access Jellyfin Dashboard:**
   - URL: `https://anduin.kooka-lake.ts.net`
   - Login as administrator

2. **Go to Dashboard → Libraries:**
   - Select your **Movies** library
   - Click **Manage Library**

3. **Configure Subtitle Settings:**
   - **Subtitle download languages:** Add your preferred languages
     - Example: `English`, `Spanish`, `French`, `German`, `Arabic`
   - **Subtitle mode:** 
     - **Smart** (recommended) - Downloads if no subtitles exist
     - **Always** - Always downloads subtitles
     - **Only if missing** - Only downloads if no subtitles found
   - **Subtitle download providers:**
     - ✅ **OpenSubtitles** (requires account)
     - ✅ **Subscene**
     - ✅ **Podnapisi**

4. **Repeat for TV Shows Library:**
   - Go to Dashboard → Libraries → TV Shows → Manage Library
   - Configure the same subtitle settings

### Configure OpenSubtitles in Jellyfin

1. **Go to Dashboard → Plugins → OpenSubtitles:**
   - Click **Settings**
   - Enter your **OpenSubtitles Username** and **Password**
   - Click **Save**

---

## 🔊 Method 3: Multiple Audio Tracks

To get media with multiple audio tracks (different languages), configure Sonarr/Radarr to prefer multi-audio releases.

### Configure Radarr (Movies)

1. **Access Radarr:**
   - URL: `https://anduin.kooka-lake.ts.net:7878`

2. **Go to Settings → Profiles:**
   - Select your quality profile
   - Click **Edit**

3. **Add Custom Formats:**
   - Go to **Settings → Custom Formats**
   - Click **Add Custom Format**
   - **Name:** `Multi-Audio`
   - **Format Tags:** Add tags like:
     - `Multi-Audio`
     - `Dual-Audio`
     - `Multi-Language`
   - **Score:** `+10` (prefers multi-audio releases)

4. **Configure Release Profiles:**
   - Go to **Settings → Indexers → Release Profiles**
   - Add **Preferred Words:**
     - `Multi-Audio` (+10)
     - `Dual-Audio` (+10)
     - `Multi-Language` (+10)

### Configure Sonarr (TV Shows)

1. **Access Sonarr:**
   - URL: `https://anduin.kooka-lake.ts.net:8989`

2. **Go to Settings → Profiles:**
   - Select your quality profile
   - Click **Edit**

3. **Add Custom Formats:**
   - Go to **Settings → Custom Formats**
   - Click **Add Custom Format**
   - **Name:** `Multi-Audio`
   - **Format Tags:** Add tags like:
     - `Multi-Audio`
     - `Dual-Audio`
     - `Multi-Language`
   - **Score:** `+10` (prefers multi-audio releases)

4. **Configure Release Profiles:**
   - Go to **Settings → Indexers → Release Profiles**
   - Add **Preferred Words:**
     - `Multi-Audio` (+10)
     - `Dual-Audio` (+10)
     - `Multi-Language` (+10)

---

## 🎯 Best Practices

### Subtitle Naming Convention

Jellyfin recognizes subtitles with these naming patterns:
- `Movie Name.en.srt` - English subtitles
- `Movie Name.es.srt` - Spanish subtitles
- `Movie Name.fr.srt` - French subtitles
- `Movie Name.ar.srt` - Arabic subtitles
- `Movie Name.eng.srt` - Alternative English format
- `Movie Name.en.forced.srt` - Forced subtitles (for foreign dialogue)

### Audio Track Selection

When media has multiple audio tracks:
1. **During Playback:**
   - Click the **Audio** button in Jellyfin player
   - Select your preferred language
   - Jellyfin remembers your preference

2. **Default Audio Language:**
   - Go to **Dashboard → Playback**
   - Set **Preferred Audio Language**
   - Set **Preferred Subtitle Language**

### Language Priority

Configure language priority in Bazarr:
1. **Go to Settings → Subtitles → Languages:**
   - **Languages to download:** Order matters!
   - First language = highest priority
   - Example order:
     1. English
     2. Spanish
     3. French
     4. Arabic

---

## 🔧 Advanced Configuration

### Bazarr Advanced Settings

1. **Go to Settings → Subtitles → Subtitles:**
   - **Hearing Impaired:** ✅ Download hearing impaired subtitles
   - **Foreign Audio Only:** ✅ Download subtitles for foreign audio only
   - **Embedded Subtitles:** ✅ Use embedded subtitles from video files
   - **Subtitle Folder:** Leave empty (stores next to media files)

2. **Go to Settings → Subtitles → Subtitles → Advanced:**
   - **Minimum Score:** `0` (accepts any match)
   - **Upgrade Previously Downloaded Subtitles:** ✅ Enabled
   - **Delete Subtitles on Media Deletion:** ✅ Enabled

### Jellyfin Playback Settings

1. **Go to Dashboard → Playback:**
   - **Preferred Audio Language:** Set your primary language
   - **Preferred Subtitle Language:** Set your primary subtitle language
   - **Subtitle Mode:** 
     - **Smart** - Downloads if missing
     - **Always** - Always downloads
     - **Only if missing** - Only if no subtitles exist

---

## 📋 Quick Setup Checklist

- [ ] Access Bazarr at `https://anduin.kooka-lake.ts.net:6767`
- [ ] Configure Sonarr integration (Host: `http://gluetun:8989`)
- [ ] Configure Radarr integration (Host: `http://gluetun:7878`)
- [ ] Enable subtitle providers (OpenSubtitles, Subscene, etc.)
- [ ] Create OpenSubtitles account and configure in Bazarr
- [ ] Set languages to download (English, Spanish, French, etc.)
- [ ] Enable automatic subtitle downloading
- [ ] Configure scheduled subtitle search (every 6 hours)
- [ ] Configure Jellyfin subtitle settings (Dashboard → Libraries)
- [ ] Configure OpenSubtitles in Jellyfin (Dashboard → Plugins)
- [ ] (Optional) Configure Sonarr/Radarr to prefer multi-audio releases
- [ ] Test by adding a new movie/show and verifying subtitles download

---

## 🎉 Summary

With Bazarr configured, you'll automatically get:
- ✅ Subtitles in your preferred languages
- ✅ Automatic downloads for new media
- ✅ Periodic updates for missing subtitles
- ✅ Support for multiple languages
- ✅ Hearing impaired subtitles (if enabled)

**Bazarr URL:** `https://anduin.kooka-lake.ts.net:6767`

Your setup is ready! Bazarr will automatically download subtitles for all your media. 🎬
