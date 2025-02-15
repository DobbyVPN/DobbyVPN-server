# Dobby VPN server

## Setup:

```bash
git clone https://github.com/DobbyVPN/DobbyVPN-server.git
cd DobbyVPN-server
./setup.sh
```

## Cloak

<details>
<summary>Cloak client config</summary>

  ```json
  {
    "Transport": "CDN",
    "ProxyMethod": "shadowsocks",
    "EncryptionMethod": "plain",
    "UID": "<your-UID-here>",
    "PublicKey": "<your-public-key-here>",
    "ServerName": "<your-server-name-here>",
    "NumConn": 8,
    "BrowserSig": "chrome",
    "StreamTimeout": 300,
    "RemoteHost": "<your-remote-host-here>",
    "RemotePort": "<your-remote-port-here>",
    "CDNWsUrlPath": "<your-cdn-ws-url-path-here>",
    "CDNOriginHost": "<your-cdn-origin-host-here>"
  }
  ```
  
  **ServerName** and **CDNWsUrlPath** have the same value, in particular, the domain name.

</details>

## AWG

### VPN docker image local build

```bash
git clone https://github.com/amnezia-vpn/amneziawg-go
cd amneziawg-go
rm Dockerfile
cp ../docker/Dockerfile-awg-server Dockerfile
docker build --no-cache -f Dockerfile -t awg-server:latest .
cd ../
```

It builds local `awg-server` image, that can be used in the [docker-compose.yaml](./docker-compose.yaml) file, for example.

### VPN management

#### List keys:

```bash
docker exec awg-server .venv/bin/python3 usrmngr/main.py list
```

#### Add key to user:

```bash
docker exec awg-server .venv/bin/python3 usrmngr/main.py list add <User>
```

#### Delete user keys:

```bash
docker exec awg-server .venv/bin/python3 usrmngr/main.py list del <User>
```

#### Get server log:

```bash
docker exec awg-server cat awg.log
```

### Config modifications:

Adding user to AWG (in file `awg/wg0.conf`, only 3 lines per user):

```bash
[Peer]
PublicKey = ...
AllowedIPs = 10.9.9.<x>/32
```

`[interface]` is filled so:

```bash
[Interface]
PrivateKey = ...
ListenPort = ...
Address = 10.9.9.1/32
Jc = ...
Jmin = ...
Jmax = ...
S1 = ...
S2 = ...
H1 = ...
H2 = ...
H3 = ...
H4 = ...

PostUp = iptables -A FORWARD -i wg0 -j ACCEPT
PostUp = iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT
PostDown = iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
```
AWG specific params (Jc, Jmin, Jmax, S1, S2, H1, H2, H3, H4) are located in `.env` file.

Environment variables are stored in `.env` file, all log information in `logs.txt` file.
Installation script: `setup.sh`. It works in an interactive mode without having to enter params via cli keys.

Warning: `setup.sh` should be executed at most once on one server, each execution after first one causes undefined behaviour.

