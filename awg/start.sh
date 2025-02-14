#!/bin/bash

# Config generation constants:
Jc_min=1
Jc_max=128
Jmin_min=40
Jmin_max=60
Jmax_max=1280
S1_max=1279
S2_max=1279
H_min=5
H_max=2147483647

# Config generation
umask 077
private_key=$(awg genkey)

if [[ -z "${AWG_LISTEN_PORT}" ]]; then
	listen_port=$(shuf -i 1025-32875 -n 1)
else
	listen_port="${AWG_LISTEN_PORT}"
fi

if [[ -z "${AWG_ADDRESS}" ]]; then
	address="10.9.9.1/32"
else
	address="${AWG_ADDRESS}"
fi

if [[ -z "${AWG_JC}" ]]; then
	Jc=$((RANDOM % (Jc_max - Jc_min + 1) + Jc_min))
else
	Jc="${AWG_JC}"
fi

if [[ -z "${AWG_JMIN}" ]]; then
	Jmin=$((RANDOM % (Jmin_max - Jmin_min + 1) + Jc_min))
else
	Jmin="${AWG_JMIN}"
fi

if [[ -z "${AWG_JMAX}" ]]; then
	Jmax=$((RANDOM % (Jmax_max - Jmin + 1) + Jmin))
else
	Jmax="${AWG_JMAX}"
fi

# S1 and S2 are unique, with condition S1 + 56 ≠ S2
if [[ -z "${AWG_S1}" ]]; then
    S1=$((RANDOM % (S1_max - 15 + 1) + 15))
else
	S1="${AWG_S1}"
fi

if [[ -z "${AWG_S2}" ]]; then
	while true; do
	    S2=$((RANDOM % (S2_max - 15 + 1) + 15))
	    if [ $((S1 + 56)) -ne $S2 ]; then
	      break
	    fi
	done
else
	S2="${AWG_S2}"
fi

# H1, H2, H3, H4 are unique between each other
if [[ -z "${AWG_H1}" ]]; then
    H1=$((RANDOM % (H_max - H_min + 1) + H_min))
else
	H1="${AWG_H1}"
fi

if [[ -z "${AWG_H2}" ]]; then
	while true; do
	    H2=$((RANDOM % (H_max - H_min + 1) + H_min))
	    if [ $H1 -ne $H2 ]; then
	      break
	    fi
	done
else
	H2="${AWG_H2}"
fi

if [[ -z "${AWG_H3}" ]]; then
	while true; do
	    H3=$((RANDOM % (H_max - H_min + 1) + H_min))
	    if [ $H1 -ne $H3 ] && [ $H2 -ne $H3 ]; then
	      break
	    fi
	done
else
	H3="${AWG_H3}"
fi

if [[ -z "${AWG_H4}" ]]; then
	while true; do
	    H4=$((RANDOM % (H_max - H_min + 1) + H_min))
	    if [ $H1 -ne $H4 ] && [ $H2 -ne $H4 ] && [ $H3 -ne $H4 ]; then
	      break
	    fi
	done
else
	H4="${AWG_H4}"
fi

cat <<EOF > wg0.conf
[Interface]
PrivateKey = $private_key
ListenPort = $listen_port
Address = $address

Jc = $Jc
Jmin = $Jmin
Jmax = $Jmax
S1 = $S1
S2 = $S2
H1 = $H1
H2 = $H2
H3 = $H3
H4 = $H4

PostUp = iptables -A FORWARD -i wg0 -j ACCEPT
PostUp = iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT
PostDown = iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
EOF

# Awg server reload cycle
config_hash=$(sha1sum wg0.conf)
echo "[$(date)] awg server up" >> awg.log
awg-quick up wg0 >> awg.log 2>&1

while true; do
	new_config_hash=$(sha1sum wg0.conf)

	if [ "$config_hash" != "$new_config_hash" ]; then
		config_hash=$new_config_hash
		echo "[$(date)] awg server down" >> awg.log
		awg-quick down wg0 >> awg.log 2>&1
		echo "[$(date)] awg server up" >> awg.log
		awg-quick up wg0 >> awg.log 2>&1
	fi

	sleep 5
done

tail -f /dev/null
