#!/bin/bash
sudo docker stop minecraft_whitelist_bot
sudo docker rm minecraft_whitelist_bot
sudo docker build -t minecraft_whitelist_bot .
sudo docker run --name minecraft_whitelist_bot -d -v /home/mdkulikowski/game_server_data/minecraft_data:/app/data minecraft_whitelist_bot
