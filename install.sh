#!/usr/bin/env bash
# shellcheck disable=SC2016,SC1090

set -ef -o pipefail

SHELL=$(basename "$SHELL")
INSTALL_PATH="/opt/dev"
VIRTUALENV_PATH="$INSTALL_PATH/venv"
PYTHON_BREW_PACKAGE="python3"
DEV_RELEASE_BRANCH="main"
GIT="git -C $INSTALL_PATH"

if [ "$(uname)" != "Darwin" ]; then
    echo "Dev require macOS"
    exit 1
fi

if [[ $SHELL != "bash" && $SHELL != "zsh" ]]; then
    echo "Dev require bash or zsh"
    exit 1
fi

if ! which -s brew; then
    echo "Dev require Homebrew - install it and try again:"
    echo ""
    echo '  bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    echo ""
    exit 1
fi

function git_clone_dev() {
    echo ""
    echo "Welcome to the Dev installer!"
    echo "You need to authenticate to create and prepare $INSTALL_PATH."
    echo ""
    sudo mkdir -p $INSTALL_PATH
    sudo chown "$USER" $INSTALL_PATH
    echo "Downloading..."
    $GIT clone --quiet --depth=1 --single-branch --branch=$DEV_RELEASE_BRANCH https://github.com/MasonData/dev.git .
    pip_install
}

function git_pull_dev() {
    echo "Downloading update..."
    $GIT fetch --quiet --depth=1 origin $DEV_RELEASE_BRANCH
    $GIT reset --quiet origin/$DEV_RELEASE_BRANCH --hard
    pip_install
}

function pip_install() {
    echo "Installing..."
    "$(brew --prefix $PYTHON_BREW_PACKAGE)/bin/$PYTHON_BREW_PACKAGE" -m venv $VIRTUALENV_PATH
    $VIRTUALENV_PATH/bin/pip install --disable-pip-version-check --quiet -e $INSTALL_PATH
}

function install_python() {
    [ -s "$(brew --prefix)/opt/$PYTHON_BREW_PACKAGE" ] && return
    echo "Installing Python..."
    brew install $PYTHON_BREW_PACKAGE
}

function install_in_shell() {
    local shell_config

    if [ "$SHELL" == "zsh" ]; then
        shell_config="$HOME/.zshrc"
    else
        shell_config="$HOME/.profile"
    fi

    local init_script='eval "$('$INSTALL_PATH'/venv/bin/dev-bare init '$SHELL')"'

    touch "$shell_config"
    grep -qxF "$init_script" "$shell_config" || echo "$init_script" >> "$shell_config"
    echo "Done! Now restart your shell to start using dev - have fun!"
}

install_python

if [ ! -d "$INSTALL_PATH/.git" ]; then
    git_clone_dev
else
    git_pull_dev
fi

install_in_shell
