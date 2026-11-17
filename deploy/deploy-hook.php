<?php
// Вебхук автодеплоя: GitHub вызывает https://ппр1.рф/_deploy.php после каждого push в main.
// Секрет не нужен: скрипт только подтягивает публичный main из GitHub, ничего не принимает от запроса.
// Повторные вызовы безопасны — внутри flock и проверка «есть ли новые коммиты».
header('Content-Type: text/plain; charset=utf-8');
$home = getenv('HOME') ?: dirname(__DIR__, 2);
$script = $home . '/ppr1rf/src/deploy/autodeploy-timeweb.sh';
if (!is_file($script)) { http_response_code(500); exit("no script\n"); }
shell_exec('nohup bash ' . escapeshellarg($script) . ' > /dev/null 2>&1 &');
echo "ok\n";
