# Trakt Integration with Jellyfin

Complete guide for integrating Trakt with Jellyfin for watch history synchronization, ratings, and collection management.

---

## 🎯 What Trakt Does with Jellyfin

Trakt integration allows you to:
- **Sync watch history**: Automatically track what you've watched in Jellyfin
- **Sync playback progress**: Resume watching across devices
- **Sync ratings**: Share your ratings between Jellyfin and Trakt
- **Import collections**: Create Jellyfin collections from your Trakt lists
- **Scrobble activity**: Real-time updates to your Trakt profile

---

## 📦 Method 1: Official Trakt Plugin (Recommended)

### Step 1: Install the Trakt Plugin

1. Access your Jellyfin dashboard:
   - URL: `https://anduin.kooka-lake.ts.net` (or your Jellyfin URL)
   - Login as an administrator

2. Navigate to **Dashboard** → **Plugins** → **Catalog**

3. Search for **"Trakt"** in the plugin catalog

4. Click **Install** on the official Trakt plugin

5. Wait for installation to complete (may take 1-2 minutes)

### Step 2: Configure Trakt Authentication

1. Go to **Dashboard** → **Plugins** → **Trakt**

2. Click on **Settings** (or the gear icon)

3. Click **Authenticate** or **Authorize with Trakt**

4. You'll see an **activation code** displayed (e.g., `ABC123XYZ`)

5. Open a new browser tab and visit: **https://trakt.tv/activate**

6. Enter the activation code and click **Authorize**

7. Return to Jellyfin - the plugin should now show "Authenticated"

### Step 3: Configure Sync Settings

In the Trakt plugin settings, configure:

**General Settings:**
- ✅ **Enable Scrobbling**: Automatically update Trakt when you watch content
- ✅ **Sync Playback Progress**: Resume watching across devices
- ✅ **Sync Ratings**: Share ratings between Jellyfin and Trakt
- ✅ **Sync Watched Status**: Keep watch history synchronized

**Sync Direction:**
- **Jellyfin → Trakt**: Send your Jellyfin activity to Trakt (recommended)
- **Trakt → Jellyfin**: Import your Trakt history to Jellyfin (optional)
- **Bidirectional**: Both directions (full sync)

**Sync Frequency:**
- **Real-time**: Updates immediately (default)
- **Periodic**: Sync every X hours (for large libraries)

### Step 4: Per-User Configuration

Each Jellyfin user can enable/disable Trakt sync:

1. Go to **Dashboard** → **Users** → Select a user
2. Scroll to **Plugins** section
3. Enable/disable Trakt sync for that specific user

---

## 🔧 Method 2: Trakt via Auto-Collections (Already Configured)

Your setup already includes Trakt integration via the `jellyfin-auto-collections` service, which can create collections from Trakt lists.

### Current Configuration

The following environment variables are already set in your `docker-compose.arr-stack.yml`:

```yaml
jellyfin-auto-collections:
  environment:
    - TRAKT_CLIENT_ID=${TRAKT_CLIENT_ID}
    - TRAKT_CLIENT_SECRET=${TRAKT_CLIENT_SECRET}
    - TRAKT_LIST_ID=${TRAKT_LIST_ID}
```

### Setting Up Trakt API Credentials

To use Trakt with auto-collections, you need to create a Trakt API application:

1. **Create Trakt API Application:**
   - Visit: https://trakt.tv/oauth/applications
   - Click **"New Application"**
   - Fill in:
     - **Name**: `Jellyfin Auto Collections` (or any name)
     - **Description**: `Auto-collections from Trakt lists`
     - **Redirect URI**: `urn:ietf:wg:oauth:2.0:oob`
   - Click **Save**

2. **Get Your Credentials:**
   - **Client ID**: Copy this value
   - **Client Secret**: Copy this value

3. **Get Your Trakt List ID:**
   - Go to your Trakt profile: https://trakt.tv/users/YOUR_USERNAME
   - Navigate to a list you want to use
   - The list ID is in the URL: `https://trakt.tv/users/USERNAME/lists/LIST_NAME`
   - Or use the list slug: `USERNAME/LIST_NAME`

4. **Add to Your `.env` File:**
   ```bash
   TRAKT_CLIENT_ID=your_client_id_here
   TRAKT_CLIENT_SECRET=your_client_secret_here
   TRAKT_LIST_ID=your_username/list_name
   ```

5. **Update via Ansible:**
   ```bash
   make ansible-deploy-arr
   ```

---

## 🎬 Using Trakt Lists with Auto-Collections

The `jellyfin-auto-collections` service can automatically create Jellyfin collections from your Trakt lists.

### Supported Trakt List Types:

- **Watchlist**: Movies/TV shows you want to watch
- **Custom Lists**: Any public or private list you create
- **Popular Lists**: Trending movies/shows on Trakt
- **User Lists**: Lists from other Trakt users

### Configuration Example:

Edit `config/jellyfin/jellyfin-plugins/auto-collections/config.yaml`:

```yaml
collections:
  - name: "Trakt Watchlist"
    type: trakt
    trakt_list: "your_username/watchlist"
    trakt_type: "movies"  # or "shows" or "both"
    
  - name: "Trakt Custom List"
    type: trakt
    trakt_list: "your_username/my-favorite-movies"
    trakt_type: "movies"
```

### Built-in Trakt Charts:

You can also use built-in Trakt charts:

```yaml
collections:
  - name: "Trending Movies"
    type: trakt
    trakt_list: "movies/trending"
    trakt_type: "movies"
    
  - name: "Popular TV Shows"
    type: trakt
    trakt_list: "shows/popular"
    trakt_type: "shows"
```

---

## 📝 Creating Trakt Lists

### Step-by-Step Process:

1. **Navigate to Your Profile:**
   - Go to https://trakt.tv/users/YOUR_USERNAME
   - Click on **"Lists"** in the navigation menu

2. **Create a New List:**
   - Click the **"+"** button or **"Add a list"** button
   - Fill in the list details

3. **List Configuration Options:**

   **Name:** 
   - Choose a descriptive name (e.g., "My Favorite Action Movies")
   - This will be the collection name in Jellyfin

   **Description:**
   - Optional: Add a description of what the list contains

   **Privacy Settings:**
   - **Private**: Only you can see it (recommended for personal lists)
   - **Link**: Only accessible via direct link
   - **Following**: Visible to people who follow you
   - **Public**: Visible to everyone

   **Collaborators:**
   - Add other Trakt users who can edit the list

   **Allow Comments:**
   - **Yes**: Others can comment on your list
   - **No**: No comments allowed

   **Display Rank:**
   - **Yes**: Show ranking numbers (1, 2, 3...)
   - **No**: No ranking displayed

   **Default Sorting:**
   - Choose how items are sorted (Rank, Title, Year, etc.)

4. **Save the List:**
   - Click **"SAVE LIST"** button

### Privacy Settings Explained

**Private** (Recommended for Personal Lists)
- **Who can see it:** Only you
- **API Access:** ✅ Yes (with authentication)
- **Use case:** Personal watchlists, private collections
- **Jellyfin auto-collections:** ✅ Works perfectly

**Link** (Good for Sharing Specific Collections)
- **Who can see it:** Only people with the direct link
- **API Access:** ✅ Yes (with authentication)
- **Use case:** Sharing specific collections with friends/family
- **Jellyfin auto-collections:** ✅ Works perfectly

**Following** (Visible to Your Followers)
- **Who can see it:** People who follow you on Trakt
- **API Access:** ✅ Yes (with authentication)
- **Use case:** Curated lists for your followers
- **Jellyfin auto-collections:** ✅ Works perfectly

**Public** (Visible to Everyone)
- **Who can see it:** Everyone on Trakt
- **API Access:** ✅ Yes (no authentication needed for public lists)
- **Use case:** Public recommendations, popular lists
- **Jellyfin auto-collections:** ✅ Works perfectly

### Special Trakt Lists

**Watchlist**
- **Format:** `username/watchlist`
- **What it is:** Your personal "want to watch" list
- **Privacy:** Automatically private (only you can see it)
- **Use case:** Movies/shows you plan to watch

**Favorites**
- **Format:** `username/favorites`
- **What it is:** Your favorite movies/shows
- **Privacy:** Can be set to any privacy level
- **Use case:** Your all-time favorites

**Custom Lists**
- **Format:** `username/list-name`
- **What it is:** Any list you create
- **Privacy:** You choose when creating
- **Use case:** Genre collections, themed lists, etc.

---

## 🔄 Sync Behavior

### What Gets Synced:

**From Jellyfin to Trakt:**
- ✅ Watch status (watched/unwatched)
- ✅ Playback progress (how far you've watched)
- ✅ Ratings (if you rate in Jellyfin)
- ✅ Collection status (if enabled)

**From Trakt to Jellyfin:**
- ✅ Watch history (if bidirectional sync enabled)
- ✅ Ratings (if bidirectional sync enabled)
- ✅ Collections (via auto-collections plugin)

### Sync Timing:

- **Real-time**: Updates happen immediately when you watch content
- **Periodic**: Full sync runs on a schedule (configurable)
- **Manual**: You can trigger a sync from the plugin settings

---

## 🛠️ Troubleshooting

### Plugin Not Appearing in Catalog

1. **Check Jellyfin Version:**
   - Trakt plugin requires Jellyfin 10.7.0 or later
   - Update Jellyfin if needed: `docker compose pull jellyfin && docker compose up -d jellyfin`

2. **Clear Plugin Cache:**
   - Stop Jellyfin: `docker stop jellyfin`
   - Remove plugin cache: `rm -rf config/jellyfin/config/plugins/cache`
   - Start Jellyfin: `docker start jellyfin`

### Authentication Fails

1. **Check Activation Code:**
   - Codes expire after 10 minutes
   - Generate a new code if expired

2. **Check Network:**
   - Ensure Jellyfin can reach `trakt.tv`
   - Check firewall rules if using VPN

3. **Check Logs:**
   ```bash
   docker logs jellyfin | grep -i trakt
   ```

### Sync Not Working

1. **Verify Settings:**
   - Ensure sync is enabled in plugin settings
   - Check per-user settings if sync is user-specific

2. **Check Permissions:**
   - Ensure the Jellyfin user has permission to modify library items
   - Check file permissions on media files

3. **Manual Sync:**
   - Go to plugin settings
   - Click "Sync Now" or "Force Sync"

### Auto-Collections Not Creating Collections

1. **Check Trakt Credentials:**
   ```bash
   docker logs jellyfin-auto-collections | grep -i trakt
   ```

2. **Verify List ID Format:**
   - Use format: `username/list-name`
   - Ensure the list is public or you have access

3. **Check Collection Schedule:**
   - Collections are created on the schedule set in `CRONTAB`
   - Default: Runs daily at 22:00 (10 PM)

---

## 📚 Additional Resources

- **Trakt Plugin GitHub**: https://github.com/jellyfin/jellyfin-plugin-trakt
- **Trakt API Documentation**: https://trakt.docs.apiary.io/
- **Jellyfin Plugin Catalog**: https://github.com/jellyfin/jellyfin-plugin-repository

---

## ✅ Quick Setup Checklist

- [ ] Install Trakt plugin from Jellyfin catalog
- [ ] Authenticate with Trakt (get activation code from plugin)
- [ ] Authorize at trakt.tv/activate
- [ ] Configure sync settings (scrobbling, progress, ratings)
- [ ] Test by watching something in Jellyfin
- [ ] Verify sync in your Trakt profile
- [ ] (Optional) Set up Trakt API credentials for auto-collections
- [ ] (Optional) Configure Trakt lists in auto-collections config

---

## 🎉 You're All Set!

Once configured, Trakt will automatically:
- Track your watch history
- Sync playback progress
- Share ratings
- Create collections from your Trakt lists (if using auto-collections)

Enjoy seamless integration between Jellyfin and Trakt! 🍿
