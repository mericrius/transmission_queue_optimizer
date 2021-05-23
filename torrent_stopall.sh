#!/bin/bash

SERVER="port --auth user:pass"

transmission-remote $SERVER --torrent all --stop
echo Stopping All Torrents
echo Excuted Time: $(date '+%Y/%m/%d %H:%M:%S')
