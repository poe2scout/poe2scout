#!/bin/bash
# Start the cron daemon
cron

# Tail the log file to keep the container running and see the output
tail -f /var/log/cron.log 