#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# URLs
RAW_INSTALL="https://raw.githubusercontent.com/hairpin01/ping-status/refs/heads/main/install.sh"
RAW_SCRIPT="https://raw.githubusercontent.com/hairpin01/ping-status/refs/heads/main/ping-status"
RAW_CONFIG="https://raw.githubusercontent.com/hairpin01/ping-status/refs/heads/main/ping_status.conf"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_blue() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_cyan() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

# Function to detect distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    elif [ -f /system/build.prop ]; then
        DISTRO="termux"
    else
        DISTRO="unknown"
    fi
    echo $DISTRO
}

# Function to install dependencies
install_dependencies() {
    local distro=$1
    
    case $distro in
        "arch" | "manjaro")
            print_status "Installing dependencies for Arch Linux..."
            sudo pacman -Syu --noconfirm
            sudo pacman -S --noconfirm python3
            ;;
        "ubuntu" | "debian" | "linuxmint")
            print_status "Installing dependencies for Ubuntu/Debian..."
            sudo apt update
            sudo apt install -y python3 python3-pip wget
            ;;
        "fedora" | "centos" | "rhel")
            print_status "Installing dependencies for Fedora/CentOS..."
            sudo dnf update -y
            sudo dnf install -y python3 python3-pip wget
            ;;
        "termux")
            print_status "Installing dependencies for Termux..."
            pkg update -y
            pkg install -y python wget
            ;;
        *)
            print_warning "Unknown distribution. Trying to proceed with system Python..."
            if ! command -v python3 &> /dev/null; then
                print_error "Python3 not found. Please install it manually."
                exit 1
            fi
            ;;
    esac
}

# Function to download file
download_file() {
    local url=$1
    local output=$2
    
    if command -v wget &> /dev/null; then
        wget -q -O "$output" "$url"
    elif command -v curl &> /dev/null; then
        curl -s -L -o "$output" "$url"
    else
        print_error "Neither wget nor curl found. Please install one of them."
        exit 1
    fi
}

# Function to setup paths based on distro
setup_paths() {
    local distro=$1
    
    if [ "$distro" = "termux" ]; then
        BIN_DIR="$PREFIX/bin"
        CONFIG_DIR="$PREFIX/etc"
        USER_CONFIG_DIR="$HOME/.config"
        PLUGINS_DIR="$HOME/.config/ping-status/plugins"
        SUDO_CMD=""
    else
        BIN_DIR="/usr/local/bin"
        CONFIG_DIR="/etc"
        USER_CONFIG_DIR="$HOME/.config"
        PLUGINS_DIR="$HOME/.config/ping-status/plugins"
        SUDO_CMD="sudo"
    fi
}

# Function to install script
install_script() {
    local distro=$1
    
    setup_paths "$distro"
    
    print_status "Downloading script from $RAW_SCRIPT..."
    download_file "$RAW_SCRIPT" "ping-status"
    
    if [ ! -f "ping-status" ]; then
        print_error "Failed to download script"
        exit 1
    fi
    
    print_status "Making script executable..."
    chmod +x ping-status
    
    print_status "Installing script to $BIN_DIR..."
    $SUDO_CMD mv -f ping-status "$BIN_DIR/"
    
    print_status "Creating symlink 'p'..."
    $SUDO_CMD ln -sf "$BIN_DIR/ping-status" "$BIN_DIR/p"
}

# Function to install config
install_config() {
    local distro=$1
    
    setup_paths "$distro"
    
    print_status "Downloading config from $RAW_CONFIG..."
    download_file "$RAW_CONFIG" "ping-status.conf"
    
    if [ ! -f "ping-status.conf" ]; then
        print_error "Failed to download config"
        exit 1
    fi
    
    print_status "Installing system-wide config to $CONFIG_DIR..."
    $SUDO_CMD mkdir -p "$CONFIG_DIR"
    $SUDO_CMD mv -f ping-status.conf "$CONFIG_DIR/"
    
    print_status "Creating user config directory..."
    mkdir -p "$USER_CONFIG_DIR"
    
    if [ ! -f "$USER_CONFIG_DIR/ping-status.conf" ]; then
        print_status "Creating user config..."
        cp "$CONFIG_DIR/ping-status.conf" "$USER_CONFIG_DIR/"
    else
        print_warning "User config already exists at $USER_CONFIG_DIR/ping-status.conf"
        print_status "Backing up existing config..."
        cp "$USER_CONFIG_DIR/ping-status.conf" "$USER_CONFIG_DIR/ping-status.conf.backup.$(date +%Y%m%d_%H%M%S)"
        print_status "You can manually update your config with new options from $CONFIG_DIR/ping-status.conf"
    fi
}

# Function to install example plugins
install_example_plugins() {
    local distro=$1
    
    setup_paths "$distro"
    
    print_status "Creating plugins directory..."
    mkdir -p "$PLUGINS_DIR"
    
    # Пример установки базовых плагинов
    print_status "Installing example plugins..."
    
    # CPU plugin
    cat > "$PLUGINS_DIR/cpu.plugin.py" << 'EOF'
#!/usr/bin/env python3

import subprocess
import os

def get_cpu_usage():
    try:
        with open('/proc/stat', 'r') as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith('cpu '):
                values = line.split()
                total = sum(int(x) for x in values[1:])
                idle = int(values[4])
                usage = 100 - (idle * 100 / total)
                return f"🖥️ {usage:.1f}%"
    except:
        return "🖥️ unknown"

def register():
    return {'cpu': get_cpu_usage()}
EOF

    # Memory plugin
    cat > "$PLUGINS_DIR/memory.plugin.py" << 'EOF'
#!/usr/bin/env python3

def get_memory_usage():
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        meminfo = {}
        for line in lines:
            key, value = line.split(':', 1)
            meminfo[key] = value.strip().split(' ')[0]
        
        total = int(meminfo['MemTotal'])
        available = int(meminfo['MemAvailable'])
        used = total - available
        usage_percent = (used / total) * 100
        return f"🧠 {used // 1024}MB ({usage_percent:.1f}%)"
    except:
        return "🧠 unknown"

def register():
    return {'memory': get_memory_usage()}
EOF

    print_status "Example plugins installed to $PLUGINS_DIR"
}

# Function to test installation
test_installation() {
    print_status "Testing installation..."
    
    if command -v p &> /dev/null; then
        print_status "Running 'p' command..."
        p
    elif command -v ping-status &> /dev/null; then
        print_status "Running 'ping-status' command..."
        ping-status
    else
        print_error "Installation failed - commands not found"
        exit 1
    fi
}

# Function to uninstall
uninstall_script() {
    local distro=$1
    
    setup_paths "$distro"
    
    print_warning "This will remove ping-status and all its files."
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Uninstallation cancelled."
        exit 0
    fi
    
    print_status "Removing files..."
    
    # Remove binary files
    $SUDO_CMD rm -f "$BIN_DIR/ping-status"
    $SUDO_CMD rm -f "$BIN_DIR/p"
    
    # Remove config files (ask for user config)
    print_status "System config removed: $CONFIG_DIR/ping-status.conf"
    
    read -p "Remove user config at $USER_CONFIG_DIR/ping-status.conf? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "$USER_CONFIG_DIR/ping-status.conf"
        print_status "User config removed."
    fi
    
    read -p "Remove plugins directory at $PLUGINS_DIR? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$PLUGINS_DIR"
        print_status "Plugins directory removed."
    fi
    
    print_status "Ping-status has been uninstalled."
}

# Function to update script
update_script() {
    print_status "Updating ping-status..."
    
    # Use the built-in update function
    if command -v ping-status &> /dev/null; then
        if sudo ping-status --update; then
            print_status "Update completed successfully!"
        else
            print_error "Update failed!"
            exit 1
        fi
    else
        print_error "ping-status not found. Please install it first."
        exit 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -s, --skip-deps     Skip dependency installation"
    echo "  -t, --skip-test     Skip installation test"
    echo "  -u, --update        Update existing installation"
    echo "  -r, --uninstall     Uninstall ping-status"
    echo "  -v, --version       Show version information"
    echo "  --with-plugins      Install example plugins"
    echo ""
    echo "Examples:"
    echo "  $0                   # Standard installation"
    echo "  $0 --with-plugins    # Install with example plugins"
    echo "  $0 --update          # Update existing installation"
}

# Function to show version
show_version() {
    echo "Ping Status Installer v3.0.0"
    echo "Author: hairpin01"
    echo "GitHub: https://github.com/hairpin01/ping-status"
}

# Main installation function
main() {
    print_cyan "🚀 Ping Status Monitor v3.0.0 Installer"
    print_cyan "   Now with Plugin System!"
    
    # Parse arguments
    SKIP_DEPS=false
    SKIP_TEST=false
    UPDATE=false
    UNINSTALL=false
    WITH_PLUGINS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -s|--skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            -t|--skip-test)
                SKIP_TEST=true
                shift
                ;;
            -u|--update)
                UPDATE=true
                shift
                ;;
            -r|--uninstall)
                UNINSTALL=true
                shift
                ;;
            -v|--version)
                show_version
                exit 0
                ;;
            --with-plugins)
                WITH_PLUGINS=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Detect distribution
    DISTRO=$(detect_distro)
    print_status "Detected distribution: $DISTRO"
    
    # Handle uninstallation
    if [ "$UNINSTALL" = true ]; then
        uninstall_script "$DISTRO"
        exit 0
    fi
    
    # Handle update
    if [ "$UPDATE" = true ]; then
        update_script
        exit 0
    fi
    
    # Install dependencies if not skipped
    if [ "$SKIP_DEPS" = false ]; then
        install_dependencies "$DISTRO"
    fi
    
    # Install script and config
    install_script "$DISTRO"
    install_config "$DISTRO"
    
    # Install plugins if requested
    if [ "$WITH_PLUGINS" = true ]; then
        install_example_plugins "$DISTRO"
    fi
    
    # Test installation if not skipped
    if [ "$SKIP_TEST" = false ]; then
        test_installation
    fi
    
    print_status "${GREEN}Installation completed successfully!${NC}"
    echo ""
    print_status "You can now use:"
    echo "  - 'p' command for quick access"
    echo "  - 'ping-status' command for full name"
    echo ""
    print_status "Available commands:"
    echo "  p                           # Show system status"
    echo "  ping-status --check-update  # Check for updates"
    echo "  ping-status --update        # Update to latest version"
    echo "  ping-status --uninstall     # Remove ping-status"
    echo "  ping-status --version       # Show version"
    echo "  ping-status --list-themes   # List available themes"
    echo "  ping-status --theme NAME    # Apply theme"
    echo "  ping-status --list-plugins  # List available plugins"
    echo "  ping-status --install-plugin NAME # Install plugin"
    echo ""
    
    if [ "$WITH_PLUGINS" = true ]; then
        print_status "Example plugins installed! Edit themes to use {cpu}, {memory} placeholders"
    else
        print_status "Install plugins later with: $0 --with-plugins"
    fi
    
    print_status "Configuration files:"
    echo "  - System-wide: $CONFIG_DIR/ping-status.conf"
    echo "  - User-specific: $USER_CONFIG_DIR/ping-status.conf"
    if [ "$WITH_PLUGINS" = true ]; then
        echo "  - Plugins: $PLUGINS_DIR/"
    fi
}

# Check if script is run with bash
if [ -z "$BASH_VERSION" ]; then
    print_error "Please run this script with bash: bash $0"
    exit 1
fi

# Run main function with all arguments
main "$@"
