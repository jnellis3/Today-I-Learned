# Connecting Docker to Tailscale VPN

Today I learned how to connect my Docker containers to a Tailscale VPN.

This setup uses a 'Sidecar' approach to integrate the Tailscale client with a Docker container, authenticated via a Tailscale authkey. Below is a complete Docker Compose configuration file that demonstrates this:

```yml
services:
  server:
    image: gitea/gitea:1.22.2
    container_name: gitea
    network_mode: service:ts-gitea
    environment:
      - USER_UID=1000
      - USER_GID=1000
    restart: always
    volumes:
      - ./gitea:/data
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro

  ts-gitea:
    image: tailscale/tailscale
    container_name: ts-gitea
    hostname: gitea
    environment:
      - TS_AUTHKEY=<KEY>
      - TS_SERVE_CONFIG=/config/gitea.json
      - TS_STATE_DIR=/var/lib/tailscale
    volumes:
      - ${PWD}/state:/var/lib/tailscale
      - ${PWD}/config:/config
      - /dev/net/tun:/dev/net/tun
    cap_add:
      - net_admin
      - sys_module
    restart: unless-stopped
```

This configuration creates a new Tailscale client container named `ts-gitea`. The key provided in the `TS_AUTHKEY` environment variable is configured to allow reuse and is ephemeral, meaning the client is automatically removed when the container is deleted.

### Setting Up HTTPS Certificates

Tailscale also supports configuring HTTPS certificates using a JSON configuration file. Ensure this feature is enabled in your Tailscale admin settings. Here’s an example configuration file:

```json
{
  "TCP": { "443": { "HTTPS": true } },
  "Web": {
    "${TS_CERT_DOMAIN}:443": {
      "Handlers": {
        "/": {
          "Proxy": "http://127.0.0.1:3000"
        }
      }
    }
  },
  "AllowFunnel": { "${TS_CERT_DOMAIN}:443": false }
}
```

Adjust the port number if necessary. This setup ensures secure HTTPS connections for your service.

By following this guide, you can effectively connect your Docker containers to a Tailscale VPN and enable HTTPS for your services.

