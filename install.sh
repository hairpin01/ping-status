#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# URLs
SCRIPT_URL="https://raw.githubusercontent.com/hairpin01/ping-status/refs/heads/main/ping-status"
CONFIG_URL="https://raw.githubusercontent.com/hairpin01/ping-status/refs/heads/main/ping_status.conf"

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
        wget -O "$output" "$url"
    elif command -v curl &> /dev/null; then
        curl -L -o "$output" "$url"
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
        SUDO_CMD=""
    else
        BIN_DIR="/usr/local/bin"
        CONFIG_DIR="/etc"
        USER_CONFIG_DIR="$HOME/.config"
        SUDO_CMD="sudo"
    fi
}

# Function to install script
install_script() {
    local distro=$1
    
    setup_paths "$distro"
    
    print_status "Downloading script from $SCRIPT_URL..."
    download_file "$SCRIPT_URL" "ping-status"
    
    print_status "Making script executable..."
    chmod +x ping-status
    
    print_status "Installing script to $BIN_DIR..."
    $SUDO_CMD mv ping-status "$BIN_DIR/"
    
    print_status "Creating symlink 'p'..."
    $SUDO_CMD ln -sf "$BIN_DIR/ping-status" "$BIN_DIR/p"
}

# Function to install config
install_config() {
    local distro=$1
    
    setup_paths "$distro"
    
    print_status "Downloading config from $CONFIG_URL..."
    download_file "$CONFIG_URL" "ping-status.conf"
    
    print_status "Installing system-wide config to $CONFIG_DIR..."
    $SUDO_CMD mkdir -p "$CONFIG_DIR"
    $SUDO_CMD mv ping-status.conf "$CONFIG_DIR/"
    
    print_status "Creating user config directory..."
    mkdir -p "$USER_CONFIG_DIR"
    
    if [ ! -f "$USER_CONFIG_DIR/ping-status.conf" ]; then
        print_status "Creating user config..."
        cp "$CONFIG_DIR/ping-status.conf" "$USER_CONFIG_DIR/"
    else
        print_warning "User config already exists at $USER_CONFIG_DIR/ping-status.conf"
        print_status "Backing up existing config..."
        cp "$USER_CONFIG_DIR/ping-status.conf" "$USER_CONFIG_DIR/ping-status.conf.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$CONFIG_DIR/ping-status.conf" "$USER_CONFIG_DIR/ping-status.conf.new"
        print_status "New config template saved as $USER_CONFIG_DIR/ping-status.conf.new"
    fi
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

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -s, --skip-deps     Skip dependency installation"
    echo "  -t, --skip-test     Skip installation test"
    echo "  -c, --config-only   Install only the config file"
    echo "  -u, --update        Update existing installation"
}

# Main installation function
main() {
    print_status "Starting ping-status installation..."
    
    # Parse arguments
    SKIP_DEPS=false
    SKIP_TEST=false
    CONFIG_ONLY=false
    UPDATE=false
    
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
            -c|--config-only)
                CONFIG_ONLY=true
                shift
                ;;
            -u|--update)
                UPDATE=true
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
    
    # Install dependencies if not skipped
    if [ "$SKIP_DEPS" = false ] && [ "$CONFIG_ONLY" = false ]; then
        install_dependencies "$DISTRO"
    fi
    
    # Install or update
    if [ "$UPDATE" = true ]; then
        print_status "Updating ping-status..."
        install_script "$DISTRO"
        install_config "$DISTRO"
    elif [ "$CONFIG_ONLY" = true ]; then
        print_status "Installing config only..."
        install_config "$DISTRO"
    else
        install_script "$DISTRO"
        install_config "$DISTRO"
    fi
    
    # Test installation if not skipped
    if [ "$SKIP_TEST" = false ] && [ "$CONFIG_ONLY" = false ]; then
        test_installation
    fi
    
    print_status "${GREEN}Installation completed successfully!${NC}"
    echo ""
    print_status "You can now use:"
    echo "  - 'p' command for quick access"
    echo "  - 'ping-status' command for full name"
    echo ""
    print_status "Configuration files:"
    echo "  - System-wide: $CONFIG_DIR/ping-status.conf"
    echo "  - User-specific: $USER_CONFIG_DIR/ping-status.conf"
    echo ""
    print_status "To customize, edit: $USER_CONFIG_DIR/ping-status.conf"
}

# Check if script is run with bash
if [ -z "$BASH_VERSION" ]; then
    print_error "Please run this script with bash: bash $0"
    exit 1
fi

# Run main function with all arguments
main "$@"
