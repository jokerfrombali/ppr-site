#!/bin/bash
# Обновить сайт ппр1.рф на хостинге Timeweb из GitHub.
# Запуск с Mac: bash deploy-timeweb.sh
# Нужен SSH-ключ ~/.ssh/id_ed25519_timeweb, добавленный в ~/.ssh/authorized_keys на хостинге.
#
# Хостинг: Timeweb, аккаунт cg50486, сервер bitrix408.timeweb.ru (185.114.247.50)
# Сайт:    ~/ppr1rf/public_html  (папка в панели: ppr1rf, домен ппр1.рф)
# Клон:    ~/ppr1rf/src  — git clone https://github.com/jokerfrombali/ppr-site.git
#
# На сервере НЕ из git и не затираются при деплое:
#   tg_config.php      — токен Telegram-бота и chat_id для уведомлений о заявках
#   zayavki.log, zayavki_no.txt — журнал и счётчик заявок
set -e
ssh -i ~/.ssh/id_ed25519_timeweb cg50486@bitrix408.timeweb.ru '
  set -e
  cd ~/ppr1rf
  [ -d src ] || git clone -q https://github.com/jokerfrombali/ppr-site.git src
  git -C src pull -q --ff-only
  git -C src log --oneline -1
  rsync -a --exclude tg_config.php --exclude zayavki.log --exclude zayavki_no.txt \
    src/production-ppr1rf/ public_html/
  echo "Готово"
'
