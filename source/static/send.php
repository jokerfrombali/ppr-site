<?php
/**
 * Обработчик форм заявок сайта ППР ПРО.
 */
declare(strict_types=1);

$TO      = 'ppr1rf@mail.ru';
$FROM    = 'noreply@xn--1-2tbae.xn--p1ai';
$SUBJECT = 'Заявка с сайта ппр1.рф';
$THANKS  = '/spasibo/';
$LOG     = __DIR__ . '/zayavki.log';
$COUNTER = __DIR__ . '/zayavki_no.txt';

// Токен и chat_id — в незакоммиченном tg_config.php прямо на хостинге (см. README),
// чтобы секрет бота не попадал в публичный git-репозиторий.
$tgConfig     = @include __DIR__ . '/tg_config.php';
$TG_TOKEN     = $tgConfig['token'] ?? '';
$TG_CHAT_ID   = $tgConfig['chat_id'] ?? '';
$TG_THREAD_ID = $tgConfig['thread_id'] ?? '';

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') { header('Location: /'); exit; }

function clean(string $v, int $max = 2000): string {
    $v = str_replace(["\r", "\n", "\0"], ' ', trim($v));
    return mb_substr(strip_tags($v), 0, $max);
}

function next_no(string $file): int {
    $fh = @fopen($file, 'c+');
    if (!$fh) { return 0; }
    flock($fh, LOCK_EX);
    $no = (int)trim((string)fread($fh, 20)) + 1;
    ftruncate($fh, 0);
    rewind($fh);
    fwrite($fh, (string)$no);
    fflush($fh);
    flock($fh, LOCK_UN);
    fclose($fh);
    return $no;
}

function tg_send(string $token, string $chatId, string $threadId, string $text): void {
    if ($token === '' || $chatId === '') { return; }
    $url = "https://api.telegram.org/bot{$token}/sendMessage";
    $params = [
        'chat_id' => $chatId, 'text' => $text,
        'parse_mode' => 'HTML', 'disable_web_page_preview' => true,
    ];
    if ($threadId !== '') { $params['message_thread_id'] = $threadId; }
    $data = http_build_query($params);
    if (function_exists('curl_init')) {
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_POST => true, CURLOPT_POSTFIELDS => $data,
            CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 5,
        ]);
        @curl_exec($ch);
        curl_close($ch);
    } else {
        $ctx = stream_context_create(['http' => [
            'method' => 'POST', 'timeout' => 5,
            'header' => "Content-Type: application/x-www-form-urlencoded\r\n",
            'content' => $data,
        ]]);
        @file_get_contents($url, false, $ctx);
    }
}

$fields = [
    'name' => 'Имя', 'phone' => 'Телефон', 'email' => 'E-mail',
    'work' => 'Вид работ / объект', 'doc_type' => 'Что нужно разработать',
    'work_type' => 'Вид работ', 'object' => 'Объект', 'deadline' => 'Срок',
    'comment' => 'Комментарий', 'page' => 'Страница', 'form' => 'Форма',
];

$name  = clean((string)($_POST['name'] ?? ''), 120);
$phone = clean((string)($_POST['phone'] ?? ''), 40);
if ($name === '' || $phone === '') { http_response_code(400); echo 'Заполните имя и телефон.'; exit; }

$no  = next_no($COUNTER);
$now = new DateTime('now', new DateTimeZone('Europe/Moscow'));
$stamp = $now->format('d.m.Y H:i:s');

$lines = ["Заявка #{$no}"];
foreach ($fields as $key => $label) {
    $val = clean((string)($_POST[$key] ?? ''));
    if ($val !== '') { $lines[] = $label . ': ' . $val; }
}
$lines[] = 'Дата: ' . $stamp . ' (Мск)';
$lines[] = 'IP: ' . ($_SERVER['REMOTE_ADDR'] ?? '');
$lines[] = 'Источник: ' . clean((string)($_SERVER['HTTP_REFERER'] ?? ''));
$body = implode("\n", $lines);

@file_put_contents($LOG, $body . "\n" . str_repeat('-', 40) . "\n", FILE_APPEND | LOCK_EX);

$replyTo = filter_var((string)($_POST['email'] ?? ''), FILTER_VALIDATE_EMAIL) ?: $FROM;
$headers = [
    'From: ' . $SUBJECT . ' <' . $FROM . '>',
    'Reply-To: ' . $replyTo,
    'Content-Type: text/plain; charset=UTF-8',
    'MIME-Version: 1.0',
];
@mail($TO, '=?UTF-8?B?' . base64_encode($SUBJECT . " #{$no}") . '?=', $body, implode("\r\n", $headers));

$page = clean((string)($_POST['page'] ?? '')) ?: clean((string)($_SERVER['HTTP_REFERER'] ?? ''));
$tg = ["\xF0\x9F\x86\x95 <b>Заявка #{$no}</b>", "\xF0\x9F\x95\x92 {$stamp} (Мск)", ''];
$tg[] = '<b>Имя:</b> ' . htmlspecialchars($name, ENT_QUOTES);
$tg[] = '<b>Телефон:</b> ' . htmlspecialchars($phone, ENT_QUOTES);
foreach (['email' => 'E-mail', 'work' => 'Вид работ / объект', 'doc_type' => 'Что нужно разработать',
          'work_type' => 'Вид работ', 'object' => 'Объект', 'deadline' => 'Срок'] as $key => $label) {
    $val = clean((string)($_POST[$key] ?? ''));
    if ($val !== '') { $tg[] = "<b>{$label}:</b> " . htmlspecialchars($val, ENT_QUOTES); }
}
$comment = clean((string)($_POST['comment'] ?? ''));
if ($comment !== '') { $tg[] = ''; $tg[] = htmlspecialchars($comment, ENT_QUOTES); }
$tg[] = '';
$tg[] = '<b>Страница:</b> ' . htmlspecialchars($page !== '' ? $page : '—', ENT_QUOTES);
tg_send($TG_TOKEN, $TG_CHAT_ID, $TG_THREAD_ID, implode("\n", $tg));

header('Location: ' . $THANKS, true, 303);
exit;
