# SSL, HTTPS, and HSTS

It's highly recommended to enable SSL/TLS on your server, both for the web app and email server.

## Using Certbot to get a certificate

This doc will use https://letsencrypt.org to get a free SSL certificate for app.mydomain.com that's used by both Postfix and Nginx. Let's Encrypt provides Certbot, a tool to obtain and renew SSL certificates.

To install Certbot, please follow instructions on https://certbot.eff.org

Then obtain a certificate for Nginx, use the following command. You'd need to provide an email so Let's Encrypt can send you notifications when your domain is about to expire.

```bash
sudo certbot --nginx
```

After this step, you should see some "managed by Certbot" lines in `/etc/nginx/sites-enabled/simplelogin`

## Using Certbot when port 80/443 is blocked

Reference: https://www.digitalocean.com/community/tutorials/how-to-acquire-a-let-s-encrypt-certificate-using-dns-validation-with-acme-dns-certbot-on-ubuntu-18-04

Install certbox

```
sudo apt-add-repository ppa:certbot/certbot
sudo apt install certbot
```

Verify install

```
certbot --version
```

Should return something like:

```
certbot 0.40.0
```

Install acme-dns-certbot

```
wget https://github.com/joohoi/acme-dns-certbot-joohoi/raw/master/acme-dns-auth.py
```

Mark the script as executable

```
chmod +x acme-dns-auth.py
```

Update script to use Python3

```
nano acme-dns-auth.py
```

Add a `3` to the end of the first line:

```
#!/usr/bin/env python3
...
```

Move the script into the Certbot Let's Encrypt directory

```
sudo mv acme-dns-auth.py /etc/letsencrypt/
```

### Setting Up acme-dns-certbot

Run Certbot to force it to issue a certificate using DNS validation. Replace `mydomain.com` with your domain name.

```
sudo certbot certonly --manual --manual-auth-hook /etc/letsencrypt/acme-dns-auth.py --preferred-challenges dns --debug-challenges -d \*.mydomain.com -d mydomain.com
```

Create a new CNAME entry as instructed:

```
Running manual-auth-hook command: /etc/letsencrypt/acme-dns-auth.py
Output from manual-auth-hook command acme-dns-auth.py:
Please add the following CNAME record to your main DNS zone:
_acme-challenge.mydomain.com CNAME xxxxb2c0-xxxx-1122-4433-5d570f6bxxxx.auth.acme-dns.io.
```

The certificate should now be created at `/etc/letsencrypt/live/mydomain.com/fullchain.pem` and private key at `/etc/letsencrypt/live/mydomain.com/privkey.pem`

See [Securing Postfix](#securing_postfix) below for the next steps. Remember to restart Postfix with `sudo systemctl restart postfix` when done.

### Updating Nginx

Instead of running `sudo certbot --nginx`, execute the following:

Create NGINX snippet

```
sudo nano /etc/nginx/snippets/dns-challenge-certbot.conf
```

Save the following text:
```
ssl_certificate /etc/letsencrypt/live/mydomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/mydomain.com/privkey.pem;

ssl_protocols TLSv1.2;
ssl_prefer_server_ciphers on;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
ssl_session_timeout 10m;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
```

Edit NGINX configuration:

```
sudo nano /etc/nginx/sites-enabled/simplelogin
```

Add the snippet to the configuration. Should look like this:

```
server {
    server_name app.mydomain.com;
    listen 443 ssl;
    listen [::]:443 ssl;

    include snippets/dns-challenge-certbot.conf;

    location / {
        proxy_pass http://localhost:7777;
    }
}
```

Restart NGINX by running `sudo systemctl reload nginx`

### <a name="securing_postfix"></a> Securing Postfix

Now let's use the new certificate for our Postfix.

Replace these lines in /etc/postfix/main.cf

```
smtpd_tls_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
smtpd_tls_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
```

with

```
smtpd_tls_cert_file = /etc/letsencrypt/live/app.mydomain.com/fullchain.pem
smtpd_tls_key_file = /etc/letsencrypt/live/app.mydomain.com/privkey.pem
```

Make sure to replace app.mydomain.com with your own domain.

### Updating `simplelogin.env`

Make sure to change the `URL` in `simplelogin.env` to `https://app.mydomain.com`, otherwise not all page assets will load securely, and some functionality (e.g. Webauthn) will break.
You will need to reload the docker containers for this to take effect.

## HTTP Strict Transport Security (HSTS)

HSTS is an extra step you can take to protect your web app from certain man-in-the-middle attacks. It does this by specifying an amount of time (usually a really long one) for which you should only accept HTTPS connections, not HTTP ones. Because of this **you should only enable HSTS once you know HTTPS is working correctly**, as otherwise you may find your browser blocking you from accessing your own web app.

To enable HSTS, add the following line to the `server` block of the Nginx configuration file:

```
add_header Strict-Transport-Security "max-age: 31536000; includeSubDomains" always;
```

(The `max-age` is the time in seconds to not permit a HTTP connection, in this case it's one year.)

Now, reload Nginx:

```bash
sudo systemctl reload nginx
```
