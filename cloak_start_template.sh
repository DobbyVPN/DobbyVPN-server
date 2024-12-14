#!/bin/bash

KEYS_PORT=<1>
CLOAK_SERVER_PORT=<2>
DOMAIN_NAME=<3>

KEYPAIRS=$(/app/ck-server -key)
CLOAK_PRIVATE_KEY=$(echo $KEYPAIRS | cut -d" " -f13)
CLOAK_PUBLIC_KEY=$(echo $KEYPAIRS | cut -d" " -f5)
USER_UID=$(/app/ck-server -uid | cut -d" " -f4)
ADMIN_UID=$(/app/ck-server -uid | cut -d" " -f4)

echo "CLOAK_PRIVATE_KEY=$CLOAK_PRIVATE_KEY" >> /app/creds.txt
echo "CLOAK_PUBLIC_KEY=$CLOAK_PUBLIC_KEY" >> /app/creds.txt
echo "USER_UID=$USER_UID" >> /app/creds.txt
echo "ADMIN_UID=$ADMIN_UID" >> /app/creds.txt

sed -i "s|<keys-port>|$KEYS_PORT|" "/app/config.json"
sed -i "s|<cloak-server-port>|$CLOAK_SERVER_PORT|" "/app/config.json"
sed -i "s|<user-UID>|$USER_UID|" "/app/config.json"
sed -i "s|<admin-UID>|$ADMIN_UID|" "/app/config.json"
sed -i "s|<domain-name>|$DOMAIN_NAME|" "/app/config.json"
sed -i "s|<cloak-private-key>|$CLOAK_PRIVATE_KEY|" "/app/config.json"


exec /app/ck-server -c /app/config.json

