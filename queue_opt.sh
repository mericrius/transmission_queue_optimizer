#!/bin/bash
python=/usr/bin/python3.9
cd $HOME/git/transmission_queue_optimizer && $python queue_opt.py >> $HOME/log/torrent_queue.log 2>&1

