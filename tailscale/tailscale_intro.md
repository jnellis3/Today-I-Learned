# Personal VPN with Tailscale

I have many self hosted sites on my LAN that I use daily (gitea, fireflyIII, etc). I always wanted to have access to them offline but didn't want to deal with the security risks associated with hosting. In addition, my personal WIFI doesn't allow for portforwarding.

I think I finally found a solution to this problem with Tailscale. This software uses wireguard as the backended and allows you to create a VPN with simple authentication through google, github, or any other authenticator service. After connecting to tailscale on a client machine, it will use "magic variables" to route traffic to vpn addresses based on the machine name. I now have connections to my iphone, desktop, aws servers, and work machine all through a VPN.

In addition to being able to access my self hosted services anywhere, I can also setup reverse proxies to host sites to the internet using my own hardware! This should save a significant amount of money as now I just need a cheap AWS server to act as the gateway.

I'm looking forward to exploring more features and inviting others to my network. The free version allows unlimited client machines and up to 3 users.