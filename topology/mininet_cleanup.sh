#!/bin/bash

echo "Kill ping sessions: "$(pidof ping)
sudo kill -9 $(pidof ping)