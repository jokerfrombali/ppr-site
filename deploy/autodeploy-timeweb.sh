#!/bin/bash
# Автодеплой ппр1.рф на Timeweb: запускается cron'ом на хостинге каждые 5 минут.
# Если на GitHub (main) есть новые коммиты — выкладывает production-ppr1rf/ в public_html.
# Не трогает: tg_config.php, zayavki.log, zayavki_no.txt.
# Журнал: ~/ppr1rf/autodeploy.log
set -e
cd ~/ppr1rf
exec 9>autodeploy.lock
flock -n 9 || exit 0
[ -d src/.git ] || git clone -q https://github.com/jokerfrombali/ppr-site.git src
git -C src fetch -q origin main
[ "$(git -C src rev-parse HEAD)" = "$(git -C src rev-parse origin/main)" ] && [ "$1" != "--force" ] && exit 0
git -C src reset -q --hard origin/main
rsync -a --exclude tg_config.php --exclude zayavki.log --exclude zayavki_no.txt \
  src/production-ppr1rf/ public_html/
echo "$(date '+%F %T') выложено $(git -C src log --oneline -1)" >> autodeploy.log
