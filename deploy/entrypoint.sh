#!/bin/sh
# Container entrypoint: prepare adb and the device, then hand over to the CLI.
#
#   ADB_SERVER_SOCKET=tcp:host.docker.internal:5037      use the host's adb server instead of our own
#   ADB_CONNECT="192.168.1.20:5555 192.168.1.21:5555"   wireless devices to `adb connect`
#   ADB_WAIT_FOR_DEVICE=1  ADB_WAIT_TIMEOUT=60           block until a device is online
#   INSTALL_ADBKEYBOARD=1                                install + enable ADBKeyboard (non-ASCII typing)
#
# `docker compose run --rm agent adb pair 192.168.1.20:37099 123456` (or sh/bash/python)
# runs that command instead of the CLI.
set -eu

# Compose passes unset variables through as "", which adb would reject as a socket spec.
if [ -z "${ADB_SERVER_SOCKET:-}" ]; then
	unset ADB_SERVER_SOCKET
fi

case "${1:-}" in
	adb | sh | bash | python | python3)
		exec "$@"
		;;
esac

if [ -n "${ADB_SERVER_SOCKET:-}" ]; then
	if ! adb devices >/dev/null 2>&1; then
		echo "entrypoint: cannot reach the adb server at $ADB_SERVER_SOCKET." >&2
		echo "  On the host run: adb kill-server, then: adb -a nodaemon server start" >&2
	fi
else
	adb start-server >/dev/null 2>&1 || echo "entrypoint: could not start the adb server" >&2
fi

host_server_hint() {
	echo "  To use devices and emulators your host's adb already sees (needed on Windows/macOS," >&2
	echo "  where Docker Desktop cannot reach USB or host emulators), share the host's adb server:" >&2
	echo "    on the host:     adb kill-server   then   adb -a nodaemon server start" >&2
	echo "    in deploy/.env:  ADB_SERVER_SOCKET=tcp:host.docker.internal:5037" >&2
}

for addr in $(echo "${ADB_CONNECT:-}" | tr ',' ' '); do
	case "$addr" in
		*:*) adb connect "$addr" || echo "entrypoint: adb connect $addr failed" >&2 ;;
		*)
			echo "entrypoint: ADB_CONNECT=$addr is a device name, not an address; skipping it." >&2
			echo "  ADB_CONNECT takes <ip>:<port> of a phone using wireless debugging." >&2
			host_server_hint
			;;
	esac
done

serial_opt=""
if [ -n "${ANDROID_AUTOMATION__DEVICE__SERIAL:-}" ]; then
	serial_opt="-s ${ANDROID_AUTOMATION__DEVICE__SERIAL}"
fi

# Only commands that drive the phone wait for it; devices/connect/check/--help do not.
case "${1:-}" in
	run | task | screenshot | ground) needs_device=1 ;;
	*) needs_device=0 ;;
esac

# shellcheck disable=SC2086 # serial_opt is intentionally split
if [ "$needs_device" = "1" ] && [ "${ADB_WAIT_FOR_DEVICE:-0}" = "1" ]; then
	if ! timeout "${ADB_WAIT_TIMEOUT:-60}" adb $serial_opt wait-for-device; then
		serial="${ANDROID_AUTOMATION__DEVICE__SERIAL:-}"
		echo "entrypoint: no device${serial:+ named $serial} after ${ADB_WAIT_TIMEOUT:-60}s." >&2
		echo "  Devices adb sees from inside the container:" >&2
		seen=$(adb devices 2>/dev/null | tail -n +2 | grep . || true)
		echo "${seen:-(none)}" | sed 's/^/    /' >&2
		if [ -n "${ADB_SERVER_SOCKET:-}" ]; then
			echo "  Using the host's adb server ($ADB_SERVER_SOCKET): run 'adb devices' on the host;" >&2
			echo "  the device must be listed there (BlueStacks: Settings > Advanced > Android Debug Bridge)." >&2
		else
			echo "  This container runs its own adb server, separate from the one on your host." >&2
			host_server_hint
			echo "  Linux + USB alternative: run 'adb kill-server' on the host so the container can claim the phone." >&2
		fi
		if [ -n "$serial" ]; then
			echo "  DEVICE_SERIAL must be one of the names listed, or empty when only one device is attached." >&2
		fi
		exit 1
	fi
fi

# shellcheck disable=SC2086
if [ "${INSTALL_ADBKEYBOARD:-0}" = "1" ] && [ "$(adb $serial_opt get-state 2>/dev/null)" = "device" ]; then
	apk="${ADBKEYBOARD_APK:-/opt/adbkeyboard/ADBKeyboard.apk}"
	if [ ! -f "$apk" ]; then
		echo "entrypoint: image built without ADBKeyboard (build arg ADBKEYBOARD=0)" >&2
	elif ! adb $serial_opt shell pm list packages 2>/dev/null | grep -q com.android.adbkeyboard; then
		if adb $serial_opt install -r "$apk"; then
			adb $serial_opt shell ime enable com.android.adbkeyboard/.AdbIME || true
		else
			echo "entrypoint: ADBKeyboard install failed; non-ASCII typing will not work" >&2
		fi
	fi
fi

exec android-automation "$@"
