#!/usr/bin/env sh
set -eu

OUT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/certs"
CRT="$OUT_DIR/server.crt"
KEY="$OUT_DIR/server.key"

mkdir -p "$OUT_DIR"

openssl req -x509 -newkey rsa:4096 -sha256 -nodes \
  -keyout "$KEY" \
  -out "$CRT" \
  -days 365 \
  -subj "/C=US/ST=Factory/L=Plant/O=ShadowPlant/OU=OT/CN=shadowplant.local"

chmod 600 "$KEY"
chmod 644 "$CRT"

echo "Generated: $CRT and $KEY"
