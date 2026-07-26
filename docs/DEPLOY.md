# Деплой video.aziral.shop

Сайт поднимается автоматически: push в `main` запускает `.github/workflows/deploy.yml`,
который по SSH заходит на сервер, обновляет код и перезапускает контейнер.

## 1. Секреты репозитория

Settings → Secrets and variables → Actions:

| Секрет | Значение |
| --- | --- |
| `SSH_HOST` | IP или домен сервера |
| `SSH_USER` | пользователь с доступом к docker |
| `SSH_PRIVATE_KEY` | приватный ключ целиком, включая строки `-----BEGIN ...-----` / `-----END ...-----` |

Без `SSH_PRIVATE_KEY` job падает с `can't connect without a private SSH key or password`.
Публичная часть ключа должна лежать в `~/.ssh/authorized_keys` пользователя `SSH_USER`.

## 2. Подготовка сервера

```bash
sudo mkdir -p /var/www
sudo git clone https://github.com/shutovBro/aziral-video-gen.git /var/www/aziral-video-gen
cd /var/www/aziral-video-gen

# внешняя сеть, к которой подключены и nginx, и приложение
docker network create fenix-global-network   # если её ещё нет

# config.toml монтируется как файл: если его нет, Docker создаст на его месте
# директорию и приложение не стартует. Workflow создаёт его сам, но при первом
# ручном запуске это нужно сделать руками.
cp config.example.toml config.toml
```

В `config.toml` пропишите ключи провайдеров (`llm_provider`, API-ключи, Pexels/Pixabay).
Файл в `.gitignore`, деплой его не перезатирает.

## 3. nginx

`nginx-site.conf` кладётся на хост-nginx (обычно `/etc/nginx/conf.d/video.aziral.shop.conf`),
затем `nginx -t && nginx -s reload`.

Контейнер nginx должен быть в сети `fenix-global-network` — иначе `proxy_pass
http://aziral-video-gen:8501` не резолвится:

```bash
docker network connect fenix-global-network <nginx-container>
```

Конфиг слушает только 80. Для HTTPS выпустите сертификат (`certbot --nginx -d video.aziral.shop`)
или терминируйте TLS на внешнем прокси.

## 4. Запуск и проверка

```bash
cd /var/www/aziral-video-gen
docker compose up -d --build
docker compose ps                       # healthy?
docker compose logs -f aziral-video-gen
curl -I http://video.aziral.shop/
```

## Диагностика

| Симптом | Причина |
| --- | --- |
| Job падает на шаге «Check deploy secrets» | не заданы SSH-секреты (см. п. 1) |
| `IsADirectoryError: config.toml` | на сервере нет `config.toml`, Docker подставил директорию |
| 502 от nginx | контейнер не запущен или nginx не в `fenix-global-network` |
| Страница грузится, но висит «Connecting…» | `STREAMLIT_BROWSER_SERVER_ADDRESS` в `docker-compose.yml` не совпадает с доменом |
