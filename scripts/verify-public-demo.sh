#!/usr/bin/env sh
set -eu

url=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --url)
      url="$2"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [ -z "$url" ]; then
  echo "--url must reference an authorized HTTPS Demo" >&2
  exit 2
fi
case "$url" in
  https://*) ;;
  *)
    echo "--url must use HTTPS" >&2
    exit 2
    ;;
esac

curl --fail --silent --show-error "$url/ready" | grep -F '"mode":"demo"'
if curl --fail --silent --show-error "$url/admin/v1/vault/status"; then
  echo "Demo must not expose Vault routes" >&2
  exit 1
fi
