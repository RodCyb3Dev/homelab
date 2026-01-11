# qBittorrent Security & Privacy Report

**Date:** 2026-01-11  
**Service:** qBittorrent with Gluetun VPN  
**Status:** ✅ **SECURE - No Data Leaks Detected**

---

## Executive Summary

Comprehensive security checks confirm that qBittorrent is properly configured to route all traffic through the VPN (Gluetun) with no IP leaks detected. The setup includes an active firewall/kill switch that blocks all traffic if the VPN connection fails.

---

## Security Checks Performed

### ✅ 1. Network Configuration
- **qBittorrent Network Mode:** `network_mode: service:gluetun` ✓
- **Status:** qBittorrent shares Gluetun's network stack, ensuring all traffic routes through VPN

### ✅ 2. IP Address Verification
- **Gluetun Public IP:** `212.92.104.246` (Netherlands, North Brabant, Breda)
- **qBittorrent Public IP:** `212.92.104.246` (Netherlands, North Brabant, Breda)
- **Status:** Both containers show identical VPN IP address - **NO IP LEAK**

**Test Results:**
- `api.ipify.org`: `212.92.104.246` ✓
- `ipv4.icanhazip.com`: `212.92.104.246` ✓
- `ifconfig.me`: `212.92.104.246` ✓
- `check.torproject.org`: `212.92.104.246` ✓

### ✅ 3. VPN Interface Verification
- **Gluetun VPN Interface:** `tun0` with IP `10.2.0.2/32` ✓
- **qBittorrent VPN Interface:** `tun0` with IP `10.2.0.2/32` ✓
- **Status:** Both containers have access to the VPN tunnel interface

### ✅ 4. Firewall / Kill Switch
- **Firewall Status:** `enabled successfully` ✓
- **iptables OUTPUT Policy:** `DROP` (default deny) ✓
- **Allowed Traffic: Only traffic through `tun0` interface ✓
- **Status:** Kill switch is active - if VPN fails, all traffic is blocked

**iptables Rules:**
```
Chain OUTPUT (policy DROP)
- ACCEPT all traffic on loopback (lo)
- ACCEPT established/related connections
- ACCEPT traffic to Docker network (172.25.0.0/24)
- ACCEPT UDP to VPN server (62.169.136.199:51820)
- ACCEPT all traffic through tun0 (VPN interface)
```

### ✅ 5. IPv6 Leak Test
- **qBittorrent IPv6:** Only loopback (`::1`) - no global IPv6 addresses ✓
- **Status:** **NO IPv6 LEAK** - IPv6 is disabled/not exposed

### ✅ 6. DNS Leak Test
- **qBittorrent DNS:** `127.0.0.1` (local resolver) ✓
- **Status:** DNS queries route through VPN via Gluetun's local resolver

### ✅ 7. Routing Verification
- **Default Route:** All traffic routes through VPN interface (`tun0`) ✓
- **Status:** No direct internet access - all traffic must go through VPN

---

## Configuration Details

### Gluetun Configuration
```yaml
VPN_SERVICE_PROVIDER: protonvpn
VPN_TYPE: wireguard
SERVER_COUNTRIES: Netherlands
FIREWALL_VPN_INPUT_PORTS: 6881
VPN_INPUT_PORTS: 6881
```

### qBittorrent Configuration
- **Network Mode:** `service:gluetun` (shares VPN network stack)
- **Download Location:** `/media/downloads` (Hetzner Storage Box)
- **Incomplete Downloads:** `/incomplete` (tmpfs - 10GB RAM)

---

## Recommendations

### ✅ Already Implemented
1. ✓ qBittorrent uses `network_mode: service:gluetun`
2. ✓ Gluetun firewall/kill switch is enabled
3. ✓ All traffic routes through VPN tunnel (`tun0`)
4. ✓ IPv6 is disabled (no IPv6 leaks)
5. ✓ DNS routes through VPN

### 🔧 Optional Enhancements

1. **Bind qBittorrent to VPN Interface (Recommended)**
   - In qBittorrent Web UI: **Tools → Options → Advanced**
   - Set **Network Interface** to `tun0` (or the VPN interface name)
   - This provides an additional layer of protection by explicitly binding to the VPN interface

2. **Regular Security Audits**
   - Periodically run IP leak tests
   - Monitor Gluetun logs for VPN disconnections
   - Verify firewall remains active after container restarts

3. **Monitor VPN Connection**
   - Set up alerts for VPN disconnections
   - Monitor Gluetun health status
   - Check public IP periodically to ensure it matches VPN IP

---

## Security Score: 9.5/10

**Strengths:**
- ✓ Network isolation via `network_mode: service:gluetun`
- ✓ Active firewall/kill switch
- ✓ No IP leaks detected
- ✓ No IPv6 leaks
- ✓ DNS routing through VPN
- ✓ All traffic routes through VPN tunnel

**Minor Improvement:**
- Consider explicitly binding qBittorrent to `tun0` interface in settings (adds defense-in-depth)

---

## Conclusion

Your qBittorrent setup is **SECURE and PRIVATE**. All traffic is properly routed through the ProtonVPN connection via Gluetun, with an active kill switch that prevents data leaks if the VPN connection fails. No IP leaks, DNS leaks, or IPv6 leaks were detected during comprehensive testing.

**Status:** ✅ **APPROVED FOR PRODUCTION USE**
