#!/bin/bash
set -euo pipefail

# ── Backup script for AI Wellness Platform SQLite database ──────────
#
# Run this via cron to create daily backups of the Docker SQLite volume.
#
#   crontab -e
#   0 3 * * * /path/to/AI_Wellness_Platform/scripts/backup_sqlite.sh
#
# ─────────────────────────────────────────────────────────────────────

BACKUP_DIR="$(cd "$(dirname "$0")/.." && pwd)/backups"
VOLUME_NAME="ai-wellness-platform_sqlite_data"
DB_FILENAME="ai_wellness.db"
RETENTION_DAYS=7

mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/wellness_db_${TIMESTAMP}.tar.gz"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting SQLite backup..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Aborting."
    exit 1
fi

# Check if the volume exists
if ! docker volume inspect "$VOLUME_NAME" > /dev/null 2>&1; then
    # Try alternative volume name pattern
    VOLUME_NAME=$(docker volume ls --format "{{.Name}}" | grep "sqlite_data" | head -1)
    if [ -z "$VOLUME_NAME" ]; then
        echo "ERROR: No SQLite volume found. Aborting."
        exit 1
    fi
    echo "  Found volume: $VOLUME_NAME"
fi

# Create a temporary container to access the volume
TEMP_CONTAINER="wellness-backup-${TIMESTAMP}"
docker run --rm \
    --name "$TEMP_CONTAINER" \
    --volume "${VOLUME_NAME}:/data" \
    alpine:latest \
    tar czf "/tmp/backup.tar.gz" -C /data "$DB_FILENAME" 2>/dev/null

# Copy the backup file out
docker cp "${TEMP_CONTAINER}:/tmp/backup.tar.gz" "$BACKUP_FILE" 2>/dev/null || {
    echo "  Using direct volume access..."
    docker run --rm \
        -v "${VOLUME_NAME}:/data" \
        -v "${BACKUP_DIR}:/backup" \
        alpine:latest \
        tar czf "/backup/wellness_db_${TIMESTAMP}.tar.gz" -C /data "$DB_FILENAME"
}

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "  Backup saved: $BACKUP_FILE ($BACKUP_SIZE)"

# Clean up old backups
echo "  Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "wellness_db_*.tar.gz" -mtime "+${RETENTION_DAYS}" -delete
REMAINING=$(find "$BACKUP_DIR" -name "wellness_db_*.tar.gz" | wc -l)
echo "  ${REMAINING} backup(s) retained."

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup complete."
