#!/bin/sh
# Backup diário do MySQL com retenção de 30 dias.
# Roda no serviço `backup` do docker-compose (imagem mysql:8.0).
set -u

BACKUP_DIR=/backups
INTERVAL="${BACKUP_INTERVAL_SECONDS:-86400}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

mkdir -p "$BACKUP_DIR"

while true; do
  ts=$(date +%Y-%m-%d_%H%M)
  file="$BACKUP_DIR/amanda-$ts.sql.gz"
  if mysqldump -h db -u root -p"$MYSQL_ROOT_PASSWORD" \
      --single-transaction --quick --routines --events \
      "$MYSQL_DATABASE" | gzip > "$file"; then
    echo "[backup] ok: $file ($(du -h "$file" | cut -f1))"
  else
    echo "[backup] FALHOU em $ts" >&2
    rm -f "$file"
  fi
  # Retenção: apaga dumps com mais de N dias.
  find "$BACKUP_DIR" -name 'amanda-*.sql.gz' -mtime "+$RETENTION_DAYS" -delete
  sleep "$INTERVAL"
done
