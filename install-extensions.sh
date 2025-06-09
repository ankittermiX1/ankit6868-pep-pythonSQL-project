#!/bin/bash
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi
mkdir -p .vscode
cat << 'SETTINGS' > .vscode/settings.json
{
    "python.testing.unittestArgs": ["-v", "-s", "./src/test", "-p", "*test*.py"],
    "python.testing.pytestEnabled": false,
    "python.testing.unittestEnabled": true,
    "extensions.ignoreRecommendations": true,
    "python.envFile": "${workspaceFolder}/.env"
}
SETTINGS
cat << 'HOOK' > .git/hooks/post-commit
#!/bin/bash
git log -1 --shortstat > history_log.txt
HOOK
chmod +x .git/hooks/post-commit
echo "PYTHONPATH=." > .env
code --install-extension revaturePro.revature-python-labs
if [ -f "src/main/lab.py" ]; then
    code -r src/main/lab.py
elif [ -f "src/main/app.py" ]; then
    code -r src/main/app.py
else
    find src/main -type f -name "*.py" | while read file; do
        code -r "$file"
    done
fi
