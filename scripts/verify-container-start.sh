#!/usr/bin/env sh
set -eu

mode=""
image=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode)
      mode="$2"
      shift 2
      ;;
    --image)
      image="$2"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [ "$mode" != "demo" ] && [ "$mode" != "private" ]; then
  echo "--mode must be demo or private" >&2
  exit 2
fi
if [ -z "$image" ]; then
  echo "--image must reference a published image" >&2
  exit 2
fi

docker pull "$image"
container_id="$(docker run --detach --rm --env "APP_MODE=$mode" --publish 127.0.0.1::8080 "$image")"
trap 'docker stop "$container_id" >/dev/null' EXIT

port="$(docker port "$container_id" 8080/tcp | sed 's/.*://')"
curl --fail --silent --show-error "http://127.0.0.1:$port/ready" >/dev/null
