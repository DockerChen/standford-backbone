#!/bin/bash

echo "Kill ping sessions: "$(pidof ping)
sudo kill -9 $(pidof ping)

echo "Kill HTTP sessions: "$(pidof SimpleHTTPServer)
sudo kill -9 $(pidof SimpleHTTPServer)