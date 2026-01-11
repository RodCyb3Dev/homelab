# Trakt List Creation and Privacy Guide

This guide explains how to create Trakt lists correctly and what privacy settings mean for use with Jellyfin auto-collections.

---

## 📋 Creating a Trakt List

### Step-by-Step Process:

1. **Navigate to Your Profile:**
   - Go to https://trakt.tv/users/YOUR_USERNAME
   - Click on **"Lists"** in the navigation menu

2. **Create a New List:**
   - Click the **"+"** button or **"Add a list"** button
   - Fill in the list details (see below)

3. **List Configuration Options:**

   **Name:** 
   - Choose a descriptive name (e.g., "My Favorite Action Movies")
   - This will be the collection name in Jellyfin

   **Description:**
   - Optional: Add a description of what the list contains
   - This helps you remember the list's purpose

   **Privacy Settings** (see details below):
   - **Private**: Only you can see it
   - **Link**: Only accessible via direct link
   - **Following**: Visible to people who follow you
   - **Public**: Visible to everyone

   **Collaborators:**
   - Add other Trakt users who can edit the list
   - Useful for shared collections

   **Allow Comments:**
   - **Yes**: Others can comment on your list
   - **No**: No comments allowed

   **Display Rank:**
   - **Yes**: Show ranking numbers (1, 2, 3...)
   - **No**: No ranking displayed

   **Default Sorting:**
   - Choose how items are sorted (Rank, Title, Year, etc.)
   - Select ascending (↑) or descending (↓) order

4. **Save the List:**
   - Click **"SAVE LIST"** button

---

## 🔒 Privacy Settings Explained

### **Private** (Recommended for Personal Lists)
- **Who can see it:** Only you
- **API Access:** ✅ Yes (with authentication)
- **Use case:** Personal watchlists, private collections
- **Jellyfin auto-collections:** ✅ Works perfectly
- **Best for:** Lists you don't want others to see

### **Link** (Good for Sharing Specific Collections)
- **Who can see it:** Only people with the direct link
- **API Access:** ✅ Yes (with authentication)
- **Use case:** Sharing specific collections with friends/family
- **Jellyfin auto-collections:** ✅ Works perfectly
- **Best for:** Lists you want to share selectively

### **Following** (Visible to Your Followers)
- **Who can see it:** People who follow you on Trakt
- **API Access:** ✅ Yes (with authentication)
- **Use case:** Curated lists for your followers
- **Jellyfin auto-collections:** ✅ Works perfectly
- **Best for:** Lists you want to share with your Trakt community

### **Public** (Visible to Everyone)
- **Who can see it:** Everyone on Trakt
- **API Access:** ✅ Yes (no authentication needed for public lists)
- **Use case:** Public recommendations, popular lists
- **Jellyfin auto-collections:** ✅ Works perfectly
- **Best for:** Lists you want to share publicly

---

## ✅ Recommended Privacy Settings for Jellyfin Auto-Collections

### For Personal Use:
- **Privacy:** **Private** or **Link**
- **Why:** Your lists are personal, and you control access
- **API Access:** Works with your Trakt API credentials

### For Sharing:
- **Privacy:** **Following** or **Public**
- **Why:** Others can discover and use your lists
- **API Access:** Works with or without authentication

---

## 🔧 Adding Lists to Jellyfin Auto-Collections

### List Format in `config.yaml`:

```yaml
trakt:
  enabled: true
  list_ids:
    - username/list-name        # Custom user list
    - username/watchlist        # User's watchlist
    - username/favorites        # User's favorites
    - "movies/trending"         # Built-in Trakt chart
    - "shows/popular"           # Built-in Trakt chart
```

### Examples:

**Your Lists:**
```yaml
- zakirpokrovskii/watchlist
- zakirpokrovskii/favorites
```

**Built-in Trakt Charts:**
```yaml
- "movies/boxoffice"      # Top box office movies
- "movies/trending"       # Trending movies
- "shows/popular"         # Popular TV shows
- "shows/trending"        # Trending TV shows
```

**Other User's Lists:**
```yaml
- username/my-awesome-list
- anotheruser/action-movies
```

---

## 📝 Special Trakt Lists

### Watchlist
- **Format:** `username/watchlist`
- **What it is:** Your personal "want to watch" list
- **Privacy:** Automatically private (only you can see it)
- **Use case:** Movies/shows you plan to watch

### Favorites
- **Format:** `username/favorites`
- **What it is:** Your favorite movies/shows
- **Privacy:** Can be set to any privacy level
- **Use case:** Your all-time favorites

### Custom Lists
- **Format:** `username/list-name`
- **What it is:** Any list you create
- **Privacy:** You choose when creating
- **Use case:** Genre collections, themed lists, etc.

---

## 🎯 Best Practices

1. **Use Descriptive Names:**
   - "My Favorite Sci-Fi Movies" ✅
   - "List 1" ❌

2. **Set Appropriate Privacy:**
   - Personal lists → **Private**
   - Shared collections → **Link** or **Following**
   - Public recommendations → **Public**

3. **Keep Lists Organized:**
   - One theme per list (e.g., "Action Movies", "Comedy Shows")
   - Use descriptions to explain the list's purpose

4. **Regular Updates:**
   - Add new items as you discover them
   - Remove items you no longer want

5. **Use Sorting:**
   - Set default sorting that makes sense (Rank, Year, Title)
   - Helps when browsing in Jellyfin

---

## 🔍 Finding List URLs

### From Trakt Website:
1. Go to your list page: `https://trakt.tv/users/username/lists/list-name`
2. The format for `config.yaml` is: `username/list-name`
3. Remove the `?sort=rank,asc` part (that's just for display)

### Example:
- **URL:** `https://trakt.tv/users/zakirpokrovskii/watchlist?sort=rank,asc`
- **Config format:** `zakirpokrovskii/watchlist`

---

## ⚙️ API Requirements

For auto-collections to work with Trakt lists, you need:

1. **Trakt API Application:**
   - Create at: https://trakt.tv/oauth/applications/new
   - Get **Client ID** and **Client Secret**

2. **Add to `.env`:**
   ```bash
   TRAKT_CLIENT_ID=your_client_id
   TRAKT_CLIENT_SECRET=your_client_secret
   ```

3. **Privacy Note:**
   - All privacy levels work with API access
   - Your API credentials authenticate you regardless of list privacy
   - Private lists require your API credentials to access

---

## 🎬 Summary

- **Privacy Settings:** Choose based on who should see your list
- **All Privacy Levels Work:** Private, Link, Following, and Public all work with auto-collections
- **Recommended:** Use **Private** for personal lists, **Link** or **Following** for sharing
- **Format:** Use `username/list-name` in config.yaml
- **Special Lists:** `username/watchlist` and `username/favorites` are built-in

Your lists are now configured in `config.yaml` and will automatically create collections in Jellyfin! 🎉
