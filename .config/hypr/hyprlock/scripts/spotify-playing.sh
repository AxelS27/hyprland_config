#!/bin/bash

if playerctl status >/dev/null 2>&1; then
    song_info=$(playerctl metadata --format '     {{title}}')
else
    song_info="     Not Playing"
fi

echo "$song_info"

