#!/usr/bin/env sh
# Install the avoid-software-falsehoods skill for Claude Code and/or Codex.
#
# Usage:
#   ./install.sh                 # install for every agent whose config dir exists
#   ./install.sh --claude        # install for Claude Code only (~/.claude/skills)
#   ./install.sh --codex         # install for Codex only (~/.codex/skills)
#   ./install.sh --all           # install for both, creating config dirs if needed
#   ./install.sh --symlink ...   # symlink the repo checkout instead of copying
#                                # (for local development; requires keeping the clone)

set -eu

SKILL_NAME="avoid-software-falsehoods"
REPO_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SKILL_SRC="$REPO_DIR/skill/$SKILL_NAME"

MODE="copy"
TARGETS=""
FORCE_ALL="no"

usage() {
    sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
    exit "${1:-0}"
}

for arg in "$@"; do
    case "$arg" in
        --claude) TARGETS="$TARGETS claude" ;;
        --codex) TARGETS="$TARGETS codex" ;;
        --all) FORCE_ALL="yes" ;;
        --symlink) MODE="symlink" ;;
        -h|--help) usage 0 ;;
        *) echo "Unknown option: $arg" >&2; usage 2 ;;
    esac
done

[ -d "$SKILL_SRC" ] || { echo "Skill source not found: $SKILL_SRC" >&2; exit 1; }

if [ -z "$TARGETS" ]; then
    if [ "$FORCE_ALL" = "yes" ]; then
        TARGETS="claude codex"
    else
        [ -d "$HOME/.claude" ] && TARGETS="$TARGETS claude"
        [ -d "$HOME/.codex" ] && TARGETS="$TARGETS codex"
        if [ -z "$TARGETS" ]; then
            echo "Neither ~/.claude nor ~/.codex exists." >&2
            echo "Pass --claude, --codex, or --all to choose an install target." >&2
            exit 1
        fi
    fi
fi

install_to() {
    dest_root="$1"
    dest="$dest_root/$SKILL_NAME"
    mkdir -p "$dest_root"
    if [ "$MODE" = "symlink" ]; then
        rm -rf "$dest"
        ln -s "$SKILL_SRC" "$dest"
        echo "Symlinked $dest -> $SKILL_SRC"
    else
        rm -rf "$dest"
        mkdir -p "$dest"
        cp -R "$SKILL_SRC/." "$dest/"
        echo "Installed $dest"
    fi
}

for target in $TARGETS; do
    case "$target" in
        claude) install_to "$HOME/.claude/skills" ;;
        codex) install_to "$HOME/.codex/skills" ;;
    esac
done

echo "Done. Restart your agent so it reloads skill metadata."
