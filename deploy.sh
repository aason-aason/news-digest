#!/bin/bash
cd ~/Desktop/news-digest
git add -A
git commit -m "update"
git pull --rebase
git push
