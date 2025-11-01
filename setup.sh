#!/bin/bash

# SupaQuery Setup Script
# This script will install Ollama and download required models

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to ask yes/no questions
ask_yes_no() {
    local prompt="$1"
    local default="${2:-y}"  # Default to 'y' if not provided

    while true; do
        if [ "$default" = "y" ]; then
            read -p "$(echo -e ${BLUE}$prompt [Y/n]: ${NC})" response
        else
            read -p "$(echo -e ${BLUE}$prompt [y/N]: ${NC})" response
        fi

        response=${response:-$default}

        case "$response" in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo -e "${YELLOW}Please answer yes or no.${NC}";;
        esac
    done
}

# Function to ask for installation method
# Returns choice via stdout: "docker" or "manual"
ask_installation_method() {
    while true; do
        echo -e "${BLUE}Which installation method would you like to use?${NC}" >&2
        echo "1) Docker (Easiest - Recommended)" >&2
        echo "2) Manual installation" >&2
        read -p "$(echo -e ${BLUE}Enter choice [1/2]: ${NC})" choice

        case "$choice" in
            1|docker|Docker|DOCKER) echo "docker"; return 0;;
            2|manual|Manual|MANUAL) echo "manual"; return 0;;
            * ) echo -e "${YELLOW}Please enter 1 for Docker or 2 for Manual.${NC}" >&2;;
        esac
    done
}

# Function to check if Ollama is running
check_ollama_running() {
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to start Ollama service
# Returns PID via stdout, status messages via stderr
start_ollama_service() {
    echo -e "${BLUE}🔄 Starting Ollama service...${NC}" >&2
    ollama serve > /dev/null 2>&1 &
    local pid=$!
    echo $pid  # Return PID to stdout
    sleep 5

    # Verify it started
    local retries=0
    while [ $retries -lt 6 ] && ! check_ollama_running; do
        retries=$((retries + 1))
        sleep 2
    done

    if check_ollama_running; then
        echo -e "${GREEN}✅ Ollama service started successfully${NC}" >&2
        return 0
    else
        echo -e "${YELLOW}⚠️  Ollama service may still be starting...${NC}" >&2
        return 0
    fi
}

# Function to install Python dependencies
install_python_deps() {
    echo ""
    echo -e "${BLUE}📦 Installing Python dependencies...${NC}"

    if [ ! -d "backend" ]; then
        echo -e "${RED}❌ Backend directory not found!${NC}"
        return 1
    fi

    cd backend

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        if ask_yes_no "Create a Python virtual environment?" "y"; then
            echo -e "${BLUE}Creating virtual environment...${NC}"
            python3 -m venv venv || python -m venv venv
        fi
    fi

    # Activate virtual environment if it exists
    VENV_ACTIVATED=false
    VENV_PIP=""

    if [ -d "venv" ]; then
        echo -e "${BLUE}Activating virtual environment...${NC}"
        if [ -f "venv/bin/activate" ]; then
            source ./venv/bin/activate
            VENV_ACTIVATED=true
            VENV_PIP="pip"
        elif [ -f "venv/Scripts/activate" ]; then
            source ./venv/Scripts/activate
            VENV_ACTIVATED=true
            VENV_PIP="pip"
        elif [ -f "venv/Scripts/pip.exe" ]; then
            echo -e "${YELLOW}⚠️  Using venv pip directly (PowerShell/CMD venv detected)${NC}"
            VENV_PIP="./venv/Scripts/pip.exe"
        elif [ -f "venv/Scripts/Activate.ps1" ] || [ -f "venv/Scripts/activate.bat" ]; then
            echo -e "${YELLOW}⚠️  Detected Windows venv, but this script is running in bash.${NC}"
            echo -e "${YELLOW}   Trying to use venv pip directly...${NC}"
            if [ -f "venv/Scripts/pip.exe" ]; then
                VENV_PIP="./venv/Scripts/pip.exe"
            else
                echo -e "${RED}❌ Cannot activate venv or find pip executable${NC}"
                echo -e "${YELLOW}   Please activate manually:${NC}"
                if [ -f "venv/Scripts/Activate.ps1" ]; then
                    echo -e "${BLUE}   PowerShell: .\venv\Scripts\Activate.ps1${NC}"
                fi
                if [ -f "venv/Scripts/activate.bat" ]; then
                    echo -e "${BLUE}   CMD: .\venv\Scripts\activate.bat${NC}"
                fi
                echo -e "${YELLOW}   Then run: pip install -r requirements.txt${NC}"
                cd ..
                return 1
            fi
        else
            echo -e "${YELLOW}⚠️  Could not find venv activation script${NC}"
        fi
    fi

    # Install requirements
    if [ -f "requirements.txt" ]; then
        if [ "$VENV_ACTIVATED" = true ] || [ -n "$VENV_PIP" ]; then
            # Use venv pip if available, otherwise system pip
            ${VENV_PIP:-pip} install -r requirements.txt
            echo -e "${GREEN}✅ Python dependencies installed${NC}"
        else
            echo -e "${YELLOW}⚠️  Installing to system Python (venv not activated)${NC}"
            pip install -r requirements.txt
            echo -e "${GREEN}✅ Python dependencies installed${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  requirements.txt not found${NC}"
    fi

    cd ..
    return 0
}

# Function to install frontend dependencies
install_frontend_deps() {
    echo ""
    echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"

    if [ ! -d "frontend" ]; then
        echo -e "${RED}❌ Frontend directory not found!${NC}"
        return 1
    fi

    cd frontend

    if [ -f "package.json" ]; then
        npm install
        echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠️  package.json not found${NC}"
    fi

    cd ..
    return 0
}

# Function to setup with Docker
setup_docker() {
    echo ""
    echo -e "${BLUE}🐳 Setting up with Docker...${NC}"

    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
        return 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
        return 1
    fi

    echo -e "${BLUE}Building and starting containers...${NC}"
    if docker compose version &> /dev/null; then
        docker compose up --build -d
    else
        docker-compose up --build -d
    fi

    echo ""
    echo -e "${GREEN}✅ Docker setup complete!${NC}"
    echo -e "${BLUE}Containers are starting in the background.${NC}"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Wait for services to start (check logs: docker compose logs -f)"
    echo "2. Download LLM model: docker exec -it supaquery-ollama ollama pull llama3.2:latest"
    echo "3. Access frontend: http://localhost:3000"
    echo "4. Access backend API: http://localhost:8000"
}

# Function to setup manually
setup_manual() {
    echo ""
    echo -e "${BLUE}🔧 Setting up manually...${NC}"

    # install python backend dependencies
    if ask_yes_no "Install Python backend dependencies?" "y"; then
        install_python_deps
    fi

    # install frontend dependencies
    if ask_yes_no "Install frontend dependencies?" "y"; then
        install_frontend_deps
    fi

    echo ""
    echo -e "${GREEN}✅ Manual setup complete!${NC}"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Start Ollama (if not running): ollama serve"
    echo "2. Start the backend: cd backend && python main.py"
    echo "3. Start the frontend: cd frontend && npm run dev"
}

# main script
echo -e "${GREEN}🚀 Setting up SupaQuery...${NC}"
echo ""

OLLAMA_PID=""
NEED_TO_KILL_OLLAMA=false

# check if ollama is installed
if ! command -v ollama &> /dev/null; then
    if ask_yes_no "📥 Ollama is not installed. Would you like to install it now?" "y"; then
        echo -e "${BLUE}📥 Installing Ollama...${NC}"
        curl -fsSL https://ollama.com/install.sh | sh
        echo -e "${GREEN}✅ Ollama installed successfully!${NC}"
    else
        echo -e "${YELLOW}⚠️  Skipping Ollama installation.${NC}"
        echo -e "${RED}❌ Setup cannot continue without Ollama. Exiting...${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Ollama is already installed${NC}"
fi

# automatically start ollama service if not running
if check_ollama_running; then
    echo -e "${GREEN}✅ Ollama service is already running${NC}"
else
    echo -e "${BLUE}🔄 Starting Ollama service automatically...${NC}"
    OLLAMA_PID=$(start_ollama_service)
    NEED_TO_KILL_OLLAMA=true
fi

echo ""

# ask about model downloads
if ask_yes_no "📦 Would you like to download the LLaMA 3.2 model? (Required - this may take a while)" "y"; then
    echo -e "${BLUE}📦 Downloading LLaMA 3.2 model (this may take a while)...${NC}"
    if ollama pull llama3.2:latest; then
        echo -e "${GREEN}✅ LLaMA 3.2 model downloaded successfully${NC}"
    else
        echo -e "${RED}❌ Failed to download LLaMA 3.2 model${NC}"
    fi
fi

echo ""

# pull mistral model (optional)
if ask_yes_no "📦 Would you like to download the Mistral model? (Optional alternative)" "n"; then
    echo -e "${BLUE}📦 Downloading Mistral model (this may take a while)...${NC}"
    if ollama pull mistral:latest; then
        echo -e "${GREEN}✅ Mistral model downloaded successfully${NC}"
    else
        echo -e "${RED}❌ Failed to download Mistral model${NC}"
    fi
fi

echo ""
echo -e "${GREEN}✅ Ollama setup complete!${NC}"
echo ""

# show downloaded models
if check_ollama_running; then
    echo -e "${BLUE}Models available:${NC}"
    ollama list
else
    echo -e "${YELLOW}⚠️  Cannot list models - Ollama service is not accessible${NC}"
fi

# automatically stop ollama service if we started it
if [ "$NEED_TO_KILL_OLLAMA" = true ] && [ -n "$OLLAMA_PID" ]; then
    echo ""
    echo -e "${BLUE}🛑 Stopping Ollama service...${NC}"
    kill $OLLAMA_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Ollama service stopped${NC}"
fi

# Ask about installation method and execute
echo ""
INSTALL_METHOD=$(ask_installation_method)

if [ "$INSTALL_METHOD" = "docker" ]; then
    setup_docker
else
    setup_manual
fi

echo ""
echo -e "${GREEN}🎉 Setup process complete!${NC}"
