#!/bin/bash

SERVER="port --auth user:pass"

result=$(transmission-remote $SERVER --torrent all -i)
id=($(awk -F ': ' '/Id: / {print $2}' <<< "$result"))
name1=$(awk -F ': ' '/Name: / {print $2}' <<< "$result")
IFS=$'\n' read -d '' -r -a name <<< $name1
public=($(awk -F ': ' '/Public torrent: / {print $2}' <<< "$result"))
done=($(awk -F ': ' '/Percent Done: / {print $2}' <<< "$result"))
state1=$(awk -F ': ' '/State: / {print $2}' <<< "$result")
IFS=$'\n' read -d '' -r -a state <<< $state1

echo -----------------------------------------------------------------------------------
printf "%-5s  %-40s  %-6s  %-6s  %-6s  %-6s\n" "Id" "Name" "Public" "Done" "State"
echo -----------------------------------------------------------------------------------
for i in "${!id[@]}"; do
    if [ "${public[$i]}" == "Yes" ]; then
        bytes=$(printf '%s' "${name[$i]}" | wc -L)
        chars=$(printf '%s' "${name[$i]}" | wc -m)
        n=$((-40+bytes-chars))
        printf "%-5s  %${n}s  %-6s  %-6s  %-6s\n" "${id[$i]}" "${name[$i]}" "${public[$i]}" "${done[$i]}" "${state[$i]}"
    fi
done
echo -----------------------------------------------------------------------------------
for i in "${!id[@]}"; do
    if [ "${public[$i]}" == "Yes" ] && [ "${done[$i]}" == "100%" ] && [ "${state[$i]}" != "Stopped" ]; then
	printf "ID: %5s / Stop  / " "${id[$i]}"
        transmission-remote $SERVER --torrent ${id[$i]} --stop
    elif [ "${public[$i]}" == "Yes" ] && [ "${done[$i]}" != "100%" ] && [ "${state[$i]}" == "Stopped" ]; then
        printf "ID: %5s / Start / " "${id[$i]}"
        transmission-remote $SERVER --torrent ${id[$i]} --start
    elif [ "${public[$i]}" == "No" ] && [ "${state[$i]}" == "Stopped" ]; then
        printf "ID: %5s / Start / " "${id[$i]}"
        transmission-remote $SERVER --torrent ${id[$i]} --start
    fi
done
echo -----------------------------------------------------------------------------------
echo Excuted Time: $(date '+%Y/%m/%d %H:%M:%S')
