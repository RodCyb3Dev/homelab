# Jellyfin Auto Collections

Automatically create and maintain collections in your Jellyfin media server based on curated lists from various sources. This plugin transforms your static media library into a dynamically organized collection system that stays up-to-date with popular lists, charts, and custom selections.

## 🎯 What It Does

Jellyfin Auto Collections automatically:
- **Scrapes curated lists** from IMDb, Letterboxd, Trakt, MDBList, and more
- **Creates collections** in Jellyfin based on these lists
- **Matches your existing media** to items in the lists
- **Updates collections** on a schedule to keep them current
- **Generates posters** for collections automatically
- **Integrates with Jellyseerr** to request missing items

## ✨ Why It's Great

### 🎬 Discover Hidden Gems
Automatically organize your library into collections like "IMDb Top 250", "1000 Greatest Films", or custom Letterboxd lists. Discover movies you already own that are part of prestigious lists.

### 🔄 Always Up-to-Date
Collections are automatically refreshed on a schedule, so new additions to your library are automatically added to relevant collections, and collections stay current with the latest charts.

### 🎨 Professional Organization
Transform your flat media library into a curated, organized experience. Collections make it easier to browse by theme, quality, or popularity.

### ⚡ Zero Manual Work
Once configured, the plugin runs automatically. No need to manually create collections or keep track of which movies belong to which lists.

### 🎯 Smart Matching
Uses advanced matching algorithms to correctly identify your media, even with slight title variations or different release years.

## 🚀 Features

### Supported List Sources

- **IMDb Charts** - Top 250, Box Office, Movie Meter, TV Meter
- **IMDb Lists** - Any public IMDb list by ID
- **Letterboxd** - Public lists from Letterboxd users
- **Trakt** - Popular lists, trending content, custom lists
- **MDBList** - Curated movie lists
- **TSPDT (They Shoot Pictures)** - 1000 Greatest Films
- **BFI (British Film Institute)** - Official BFI lists
- **Criterion Channel** - Criterion collection lists
- **Radarr/Sonarr** - Collections based on tags in your *arr stack
- **Jellyfin API** - Custom queries using Jellyfin's API
- **Popular Movies** - Trending movies from various sources

### Key Capabilities

- ✅ **Automatic Collection Creation** - Creates collections if they don't exist
- ✅ **Smart Media Matching** - Matches movies/shows even with title variations
- ✅ **Scheduled Updates** - Runs on a cron schedule (default: daily at 22:00)
- ✅ **Collection Clearing** - Option to clear and rebuild collections (useful for dynamic lists)
- ✅ **Poster Generation** - Automatically generates posters for collections
- ✅ **Jellyseerr Integration** - Automatically requests missing items via Jellyseerr
- ✅ **Year Filtering** - Option to match only exact release years or allow flexibility
- ✅ **Multiple Collections** - Support for unlimited collections from multiple sources

## 📋 Requirements

- Jellyfin server (accessible via API)
- Jellyfin API key (create in Dashboard → Advanced → API Keys)
- Jellyfin User ID (found in user profile URL)
- Docker (for containerized deployment)
- Python 3.10+ (if running directly)

## 🔧 Configuration

### Basic Configuration

Edit `config.yaml`:

```yaml
crontab: 0 22 * * *   # Daily at 22:00 (cron format)
timezone: Europe/Helsinki

jellyfin:
  server_url: https://your-jellyfin-server.com
  api_key: your-api-key-here
  user_id: your-user-id-here

plugins:
  imdb_chart:
    enabled: true
    list_ids:
      - top          # IMDb Top 250
      - boxoffice    # Box Office charts
    clear_collection: true  # Clear before rebuilding
```

### Environment Variables

The plugin supports environment variables for sensitive data:

```yaml
jellyfin:
  server_url: !ENV ${JELLYFIN_SERVER_URL:https://anduin.kooka-lake.ts.net}
  api_key: !ENV ${JELLYFIN_API_KEY:your-default-key}
  user_id: !ENV ${JELLYFIN_USER_ID:your-user-id}
```

### Plugin Configuration Examples

#### IMDb Top 250
```yaml
imdb_chart:
  enabled: true
  list_ids:
    - top
    - boxoffice
    - moviemeter
    - tvmeter
  clear_collection: true
```

#### Letterboxd Lists
```yaml
letterboxd:
  enabled: true
  imdb_id_filter: true  # Better matching, slower
  list_ids:
    - username/list-name
    - another-user/another-list
```

#### Trakt Lists
```yaml
trakt:
  enabled: true
  client_id: your-trakt-client-id
  client_secret: your-trakt-client-secret
  list_ids:
    - "movies/boxoffice"
    - "shows/popular"
    - custom-list-id
```

#### Radarr/Sonarr Tags
```yaml
arr:
  enabled: true
  server_configs:
    - base_url: http://radarr:7878
      api_key: radarr-api-key
    - base_url: http://sonarr:8989
      api_key: sonarr-api-key
  list_ids:
    - my-tag-name  # Creates collection from items with this tag
```

## 🐳 Docker Deployment

### Using Docker Compose

```yaml
jellyfin-auto-collections:
  build:
    context: ./jellyfin-plugins/auto-collections
    dockerfile: Dockerfile
  container_name: jellyfin-auto-collections
  network_mode: service:ts-anduin  # Or your network
  env_file:
    - .env
  environment:
    - JELLYFIN_SERVER_URL=${JELLYFIN_URL}
    - JELLYFIN_API_KEY=${JELLYFIN_API_KEY}
    - JELLYFIN_USER_ID=${JELLYFIN_USER_ID}
  volumes:
    - ./jellyfin-plugins/auto-collections/config.yaml:/app/config/config.yaml
  restart: unless-stopped
```

### Building the Image

```bash
docker-compose build jellyfin-auto-collections
docker-compose up -d jellyfin-auto-collections
```

## 📖 Usage Examples

### Example 1: IMDb Top 250 Collection

Create a collection of all movies from your library that are in the IMDb Top 250:

```yaml
imdb_chart:
  enabled: true
  list_ids:
    - top
  clear_collection: true
```

Result: A collection named "IMDb Top 250 movies" containing all matching movies from your library.

### Example 2: Custom Letterboxd List

Follow a specific Letterboxd user's curated list:

```yaml
letterboxd:
  enabled: true
  list_ids:
    - username/movies-everyone-should-watch
```

Result: A collection matching that user's list with your existing media.

### Example 3: Trakt Trending

Keep a collection of currently trending movies:

```yaml
trakt:
  enabled: true
  list_ids:
    - "movies/boxoffice"
  clear_collection: true  # Rebuild daily to stay current
```

### Example 4: Radarr Tagged Movies

Create collections based on tags in Radarr:

```yaml
arr:
  enabled: true
  server_configs:
    - base_url: http://radarr:7878
      api_key: your-key
  list_ids:
    - "action"
    - "comedy"
    - "horror"
```

Result: Separate collections for each tag.

## 🎨 How It Works

1. **List Scraping**: The plugin connects to various APIs and scrapes curated lists
2. **Media Matching**: It searches your Jellyfin library for matching titles
3. **Collection Management**: Creates or updates collections with matched items
4. **Scheduled Updates**: Runs on a cron schedule to keep collections current
5. **Missing Items**: Optionally requests missing items via Jellyseerr

## 🔍 Troubleshooting

### Collections Not Appearing

- Check Jellyfin API key is valid
- Verify user ID is correct
- Check logs: `docker logs jellyfin-auto-collections`
- Ensure media is properly matched (check titles match)

### Items Not Matching

- Enable `imdb_id_filter: true` for better matching (slower)
- Check year filtering settings
- Verify movie titles in Jellyfin match list titles

### Jellyseerr Integration

Jellyseerr is optional. If unavailable, the plugin will continue without it:
```
WARNING - Jellyseerr is not available: ... Continuing without Jellyseerr integration.
```

## 📝 Best Practices

1. **Start Small**: Enable one plugin at a time to test
2. **Use Clear Collections**: Enable `clear_collection: true` for dynamic lists (charts, trending)
3. **Disable for Static Lists**: Keep `clear_collection: false` for curated lists that don't change
4. **Schedule Wisely**: Run during off-peak hours (default: 22:00)
5. **Monitor Logs**: Check logs regularly to ensure proper operation

## 🔗 Integration with Jellyseerr

When enabled, the plugin can automatically request missing items:

```yaml
jellyseerr:
  server_url: https://your-jellyseerr.com
  email: your-email
  username: your-username
  password: your-password
  user_type: local
```

When an item from a list isn't found in your library, it will be automatically requested via Jellyseerr.

## 🎯 Use Cases

- **Film Enthusiasts**: Organize your library by prestigious lists (IMDb Top 250, TSPDT 1000)
- **Content Curators**: Follow specific Letterboxd users' lists
- **Trend Watchers**: Keep collections of trending/box office hits
- **Tag-Based Organization**: Use Radarr/Sonarr tags to create collections
- **Custom Queries**: Use Jellyfin API to create collections based on any criteria

## 📚 Supported Sources

| Source | Type | Description |
|--------|------|-------------|
| IMDb Charts | Charts | Top 250, Box Office, Movie/TV Meter |
| IMDb Lists | Lists | Any public IMDb list |
| Letterboxd | Lists | Public user lists |
| Trakt | Lists/Charts | Popular, trending, custom lists |
| MDBList | Lists | Curated movie lists |
| TSPDT | Lists | 1000 Greatest Films |
| BFI | Lists | British Film Institute official lists |
| Criterion | Lists | Criterion Channel collections |
| Radarr/Sonarr | Tags | Collections from *arr tags |
| Jellyfin API | Queries | Custom API queries |
| Popular Movies | Charts | Trending movies |

## 🛠️ Development

This plugin is built with:
- Python 3.10+
- APScheduler for cron scheduling
- PluginLib for extensible plugin system
- Requests for API calls
- PyYAML for configuration

### Adding Custom Plugins

Plugins follow the base plugin interface:

```python
@pluginlib.Parent('list_scraper')
class MyCustomPlugin(object):
    @pluginlib.abstractmethod
    def get_list(list_id, config=None):
        return {
            "name": "My List",
            "description": "Description",
            "items": [...]
        }
```

## 📄 License

This project is open source. Check the original repository for license details.

## 🙏 Credits

Based on [Jellyfin Auto Collections](https://github.com/ghomasHudson/jellyfin-auto-collections) by ghomasHudson.

---

**Enjoy your automatically organized Jellyfin library! 🎬✨**
