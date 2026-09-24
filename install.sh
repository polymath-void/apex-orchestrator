#!/usr/bin/env bash
set -e

echo "🧠 Installing Apex Rage Engine Plugin..."

# 1. Determine the target plugin directory
AGY_CONFIG_DIR="${HOME}/.gemini/config"
PLUGINS_DIR="${AGY_CONFIG_DIR}/plugins"
TARGET_DIR="${PLUGINS_DIR}/apex"

mkdir -p "$PLUGINS_DIR"

# 2. Check if we are already in the target directory
CURRENT_DIR="$(pwd)"
if [[ "$CURRENT_DIR" != "$TARGET_DIR" ]]; then
    echo "📦 Copying files to $TARGET_DIR..."
    rm -rf "$TARGET_DIR"
    cp -r "$CURRENT_DIR" "$TARGET_DIR"
fi

# 3. Dynamically generate hooks.json with the correct absolute path
HOOKS_FILE="${TARGET_DIR}/hooks.json"
WRAPPER_PATH="${TARGET_DIR}/hook_wrapper.py"

echo "🔗 Generating dynamic hooks.json..."
cat <<EOF > "$HOOKS_FILE"
{
  "apex-intercept": {
    "enabled": true,
    "PreInvocation": [
      {
        "type": "command",
        "command": "python3 $WRAPPER_PATH",
        "timeout": 300
      }
    ]
  }
}
EOF

echo "✅ Apex Rage Engine successfully installed!"
echo "   Location: $TARGET_DIR"
echo "   To use it, just type: agy -p \"/apex <your prompt>\""
