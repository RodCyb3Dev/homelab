#!/bin/bash
##############################################################################
# JELLYFIN PERFORMANCE CHECK SCRIPT
# Monitors system and Jellyfin performance during playback
##############################################################################

set -e

HOMELAB_DIR="/opt/homelab"
SSH_KEY="${SSH_KEY:-~/.ssh/ansible_key}"
SSH_USER="${SSH_USER:-rodkode}"
SSH_HOST="${SSH_HOST:-95.216.176.147}"

echo "🎬 Jellyfin Performance Check"
echo "=============================="
echo ""

# System Performance
echo "📊 SYSTEM PERFORMANCE"
echo "----------------------"
ssh -i "${SSH_KEY}" "${SSH_USER}@${SSH_HOST}" << 'EOF'
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | head -1
echo ""
echo "Memory Usage:"
free -h
echo ""
echo "System Load:"
uptime
echo ""
echo "Disk Usage:"
df -h / | tail -1
EOF

echo ""
echo "🐳 DOCKER CONTAINER STATS"
echo "-------------------------"
ssh -i "${SSH_KEY}" "${SSH_USER}@${SSH_HOST}" "sudo docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}' | head -15"

echo ""
echo "🎥 JELLYFIN METRICS"
echo "-------------------"
ssh -i "${SSH_KEY}" "${SSH_USER}@${SSH_HOST}" << 'EOF'
echo "Active Sessions:"
sudo docker exec jellyfin curl -s http://localhost:8096/Sessions 2>/dev/null | python3 -m json.tool 2>/dev/null | grep -E '"UserName"|"Client"|"NowPlayingItem"|"PlayState"' | head -20 || echo "No active sessions or API not accessible"
echo ""
echo "Transcoding Cache Usage:"
sudo docker exec jellyfin df -h /config/data/transcodes 2>/dev/null || echo "tmpfs not mounted"
echo ""
echo "Jellyfin Container Health:"
sudo docker inspect jellyfin --format '{{.State.Health.Status}}' 2>/dev/null || echo "No healthcheck configured"
EOF

echo ""
echo "📈 NETWORK ACTIVITY"
echo "-------------------"
ssh -i "${SSH_KEY}" "${SSH_USER}@${SSH_HOST}" "sudo ss -tunp 2>/dev/null | grep -E '8096|5000|8000' | head -10 || echo 'No active connections on Jellyfin ports'"

echo ""
echo "📝 RECENT JELLYFIN LOGS"
echo "-----------------------"
ssh -i "${SSH_KEY}" "${SSH_USER}@${SSH_HOST}" "sudo docker logs jellyfin --tail 30 2>&1 | grep -E 'transcod|playback|stream|ffmpeg' | tail -10 || echo 'No relevant logs found'"

echo ""
echo "✅ Performance check complete!"
echo ""
echo "💡 Tips:"
echo "  - CPU usage should be < 80% during transcoding"
echo "  - Memory usage should be < 90%"
echo "  - Transcoding cache (tmpfs) should show usage if transcoding"
echo "  - Check for 'ffmpeg' processes if transcoding is active"
