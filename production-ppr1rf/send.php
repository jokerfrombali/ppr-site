<?php
/**
 * Обработчик форм заявок сайта ППР ПРО.
 * ПЕРЕД ЗАПУСКОМ: проверьте $TO и $FROM (адрес отправителя должен быть на вашем домене).
 */
declare(strict_types=1);

$TO      = '5608018@mail.ru';
$FROM    = 'noreply@xn--1-2tbae.xn--p1ai';
$SUBJECT = 'Заявка с сайта ппр1.рф';
$THANKS  = '/spasibo/';
$LOG     = __DIR__ . '/zayavki.log';

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') { header('Location: /'); exit; }

function clean(string $v, int $max = 2000): string {
    $v = str_replace(["\r", "\n", "\0"], ' ', trim($v));
    return mb_substr(strip_tags($v), 0, $max);
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

$lines = [];
foreach ($fields as $key => $label) {
    $val = clean((string)($_POST[$key] ?? ''));
    if ($val !== '') { $lines[] = $label . ': ' . $val; }
}
$lines[] = 'Дата: ' . date('d.m.Y H:i');
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
@mail($TO, '=?UTF-8?B?' . base64_encode($SUBJECT) . '?=', $body, implode("\r\n", $headers));

header('Location: ' . $THANKS, true, 303);
exit;
