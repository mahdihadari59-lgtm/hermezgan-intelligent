#!/bin/bash

echo "🚀 Starting Hermezgan Intelligent System..."
echo ""

# رنگ‌ها
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# تابع برای کشتن فرآیندها
cleanup() {
    echo -e "\n${RED}🛑 Shutting down all services...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit
}

# گرفتن سیگنال‌ها
trap cleanup SIGINT SIGTERM

# ۱. Bandari Engine
echo -e "${BLUE}📡 Starting Bandari Engine...${NC}"
cd ~/hermezgan-intelligent/bandari-engine-2026/bandari-engine
npm start &
BANDARI_PID=$!

sleep 3

# ۲. HDP API Server
echo -e "${BLUE}🚀 Starting HDP API Server...${NC}"
cd ~/hermezgan-intelligent/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

echo -e "\n${GREEN}✅ All services started!${NC}"
echo -e "   📡 Bandari Engine: ${YELLOW}http://localhost:5200${NC}"
echo -e "   🚀 HDP API Server: ${YELLOW}http://localhost:8000${NC}"
echo -e ""
echo -e "📋 تست سریع:"
echo -e "   ${BLUE}curl http://localhost:8000/api/v1/speech/status${NC}"
echo -e "   ${BLUE}curl -X POST http://localhost:8000/api/v1/speech/process -F 'text=بندرعباس کجاست؟' -F 'user_id=test'${NC}"
echo -e ""
echo -e "${GREEN}Press Ctrl+C to stop all services${NC}"

wait
