# Reverse Proxy using Caddy

When hosting at home you may want to use a reverse proxy configuration, where requests terminate on a public facing server, routing to your internal network

## Caddy configuration

Install Caddy

```
sudo apt update
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

Edit Caddy configuration file

```
sudo nano /etc/caddy/Caddyfile
```

Enter the reverse proxy configuration and replace `app.mydomain.com` with your domain name and `xxx.xxx.xxx.xxx` with your server at home's IP address. The port `7443` may be replaced with your router's forwarded port.

```
app.mydomain.com {
        # Set this path to your site's directory.
        # root * /usr/share/caddy

        # Enable the static file server.
        # file_server

        # Another common task is to set up a reverse proxy:
        reverse_proxy https://xxx.xxx.xxx.xxx:7443 {
            transport http {
                tls_insecure_skip_verify
            }
        }
}
```

Restart Caddy by running `sudo systemctl reload caddy`