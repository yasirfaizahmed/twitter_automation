#!/bin/sh
# Container entrypoint: prepare adb and the device, then hand over to the CLI.
#
#   ADB_CONNECT="192.168.1.20:5555 192.168.1.21:5555"   wireless devices to `adb connect`
#   ADB_WAIT_FOR_DEVICE=1  ADB_WAIT_TIMEOUT=60           block until a device is online
#   INSTALL_ADBKEYBOARD=1                                install + enable ADBKeyboard (non-ASCII typing)
#
# `docker compose run --rm agent adb pair 192.168.1.20:37099 123456` (or sh/bash/python)
# runs that command instead of the CLI.
set -eu

case "${1:-}" in
	adb | sh | bash | python | python3)
		exec "$@"
		;;
esac

adb start-server >/dev/null 2>&1 || echo "entrypoint: could not start the adb server" >&2

for addr in $(echo "${ADB_CONNECT:-}" | tr ',' ' '); do
	adb connect "$addr" || echo "entrypoint: adb connect $addr failed" >&2
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
		echo "entrypoint: no device after ${ADB_WAIT_TIMEOUT:-60}s (USB: run 'adb kill-server' on the host; Wi-Fi: set ADB_CONNECT)" >&2
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
