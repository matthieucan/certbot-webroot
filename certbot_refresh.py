#!/usr/bin/python3
import os
import subprocess


# Call certbot program to refresh all live certificates.
def certbot_renew():
    print('## Renewing certificates files using certbot ##')
    result = subprocess.run("certbot renew",
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
    return ('The following certs were successfully renewed' in result.stdout or
            'Congratulations, all renewals succeeded. The following certs have been renewed' in result.stdout)


# Generate haproxy.pem aggregate files of fullchain.pem and privkey.pem for each directory in /etc/letsencrypt/live
def generate_haproxy():
    print('## Generating haproxy files ##')
    if not os.path.exists('/etc/letsencrypt/live'):
        return

    for entry in os.scandir('/etc/letsencrypt/live'):
        if entry.is_file():
            continue

        certificate_path = os.path.join(entry.path, 'haproxy.pem')
        fullchain_path = os.path.join(entry.path, 'fullchain.pem')
        privkey_path = os.path.join(entry.path, 'privkey.pem')
        if os.path.exists(certificate_path):
            os.remove(certificate_path)
        if os.path.exists(fullchain_path) and os.path.exists(privkey_path):
            os.system('cat {0} {1} > {2}'.format(privkey_path, fullchain_path, certificate_path))


# Reload haproxy
def reload_haproxy():
    print('## Reloading haproxy ##')
    subprocess.run(["service haproxy reload"],
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)


# Main program to call in cron job
if __name__ == "__main__":
    if certbot_renew():
        generate_haproxy()
        reload_haproxy()
    else:
        print('No certificate renewed, no reload is necessary.')
