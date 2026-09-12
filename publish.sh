#!/bin/bash
# Публикация сайта в GitHub. Запуск: bash publish.sh [имя-репозитория]
set -e
REPO="${1:-ppr-pro-site}"
USER="jokerfrombali"
cd "$(dirname "$0")"
git remote remove origin 2>/dev/null || true
git remote add origin "git@github.com:$USER/$REPO.git"
git push -u origin main
echo
echo "Готово. Осталось включить GitHub Pages:"
echo "  https://github.com/$USER/$REPO/settings/pages"
echo "  Source: Deploy from a branch → Branch: main → / (root) → Save"
echo
echo "Через 1–2 минуты сайт откроется здесь:"
echo "  https://$USER.github.io/$REPO/"
