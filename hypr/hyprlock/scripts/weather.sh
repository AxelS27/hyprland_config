#!/usr/bin/env bash

CITY=$(grep '^\$CITY' ~/.config/hypr/hyprlock/hyprlock.conf | cut -d'=' -f2 | xargs)
COUNTRY=$(grep '^\$COUNTRY' ~/.config/hypr/hyprlock/hyprlock.conf | cut -d'=' -f2 | xargs)

if [[ -z "$CITY" || -z "$COUNTRY" ]]; then
    echo "Error: Unable to determine your location from hyprlock.conf"
    exit 1
fi

weather_info=$(curl -s --fail "https://en.wttr.in/$CITY?format=%c+%t" 2>/dev/null)

if [[ $? -ne 0 || -z "$weather_info" ]]; then
    echo "Error: Failed to retrieve weather info for $COUNTRY, $CITY"
    exit 1
fi

echo "$weather_info"

