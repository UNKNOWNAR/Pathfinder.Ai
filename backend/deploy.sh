#!/bin/bash

# Configuration
PROJECT_ROOT="/home/ubuntu/Pathfinder.Ai"
APP_DIR="$PROJECT_ROOT/backend"
VENV_PATH="$APP_DIR/venv"
ACCESS_LOG="/home/ubuntu/access.log"
ERROR_LOG="/home/ubuntu/error.log"

echo "🚀 Starting Pathfinder.Ai Production Sync..."

# 1. Update Code from GitHub (from the Root)
cd "$PROJECT_ROOT" || exit
echo "📥 Pulling latest code from master..."
git pull origin master

# 2. Enter Backend Directory for App tasks
cd "$APP_DIR" || exit

# 2. Activate Virtual Environment
source "$VENV_PATH/bin/activate"

# 3. Kill existing Gunicorn processes safely
echo "🛑 Stopping old server..."
pkill gunicorn
sudo fuser -k 5000/tcp

# 4. Start the new Server as a Daemon
echo "🔥 Launching new Gunicorn workers..."
gunicorn --workers 3 \
         --bind 127.0.0.1:5000 \
         --access-logfile "$ACCESS_LOG" \
         --error-logfile "$ERROR_LOG" \
         --daemon \
         app:app

# 5. Success Check
sleep 2
if ps aux | grep -v grep | grep gunicorn > /dev/null
then
    echo "✅ SUCCESS: Pathfinder.Ai is LIVE at https://pathfinderai.me"
    echo "📜 Logs: tail -f ~/access.log"
else
    echo "❌ ERROR: Server failed to start. Check ~/error.log"
fi
