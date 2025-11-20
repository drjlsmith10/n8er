#!/bin/bash

###############################################################################
# Project Automata: Knowledge Base Backup Script
#
# Usage: ./backup_knowledge_base.sh [backup_dir] [retention_days]
#
# Args:
#   backup_dir: Directory to store backups (default: ./backups)
#   retention_days: Number of days to keep backups (default: 30)
#
# Features:
#   - Creates timestamped backup archives
#   - Compresses with gzip for efficient storage
#   - Verifies backup integrity
#   - Cleans up old backups automatically
#   - Creates backup manifest with metadata
#
# Author: Project Automata
# Version: 1.0.0
# Created: 2025-11-20
###############################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${1:-$PROJECT_DIR/backups}"
RETENTION_DAYS="${2:-30}"

# Paths to backup
KB_DIR="$PROJECT_DIR/knowledge_base"
WORKFLOWS_DIR="$PROJECT_DIR/workflows"
LOGS_DIR="$PROJECT_DIR/logs"

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="automata_backup_${TIMESTAMP}"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

###############################################################################
# Logging functions
###############################################################################

log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

###############################################################################
# Backup functions
###############################################################################

check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v tar &> /dev/null; then
        log_error "tar not found. Please install tar."
        exit 1
    fi

    if ! command -v gzip &> /dev/null; then
        log_error "gzip not found. Please install gzip."
        exit 1
    fi

    if [[ ! -d "$KB_DIR" ]]; then
        log_warn "Knowledge base directory not found: $KB_DIR"
    fi

    log_info "All prerequisites met"
}

create_backup_dir() {
    if [[ ! -d "$BACKUP_DIR" ]]; then
        log_info "Creating backup directory: $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
    fi
}

create_backup_archive() {
    log_info "Creating backup archive: $BACKUP_PATH.tar.gz"

    # Create tarball with compression
    tar -czf "$BACKUP_PATH.tar.gz" \
        -C "$PROJECT_DIR" \
        --exclude='__pycache__' \
        --exclude='.pytest_cache' \
        --exclude='.git' \
        --exclude='.env' \
        --exclude='*.pyc' \
        --exclude='*.pyo' \
        --exclude='*.pyd' \
        --exclude='.DS_Store' \
        knowledge_base/ \
        workflows/ \
        logs/ \
        config.py \
        requirements.txt \
        2>/dev/null || {
        log_error "Failed to create backup archive"
        return 1
    }

    if [[ -f "$BACKUP_PATH.tar.gz" ]]; then
        log_info "Backup archive created successfully"
        return 0
    else
        log_error "Backup archive was not created"
        return 1
    fi
}

verify_backup() {
    log_info "Verifying backup integrity..."

    if tar -tzf "$BACKUP_PATH.tar.gz" > /dev/null 2>&1; then
        log_info "Backup integrity verified"
        return 0
    else
        log_error "Backup integrity verification failed"
        return 1
    fi
}

create_manifest() {
    log_info "Creating backup manifest..."

    MANIFEST_FILE="$BACKUP_PATH.manifest"

    {
        echo "# Project Automata Backup Manifest"
        echo "# Created: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo ""
        echo "Backup Name: $BACKUP_NAME"
        echo "Backup Path: $BACKUP_PATH.tar.gz"
        echo "Timestamp: $TIMESTAMP"
        echo "Archive Size: $(du -h "$BACKUP_PATH.tar.gz" | cut -f1)"
        echo ""
        echo "## Contents"
        echo "- knowledge_base/ (Community learned patterns, error solutions)"
        echo "- workflows/ (Generated and sample workflows)"
        echo "- logs/ (Application logs)"
        echo "- config.py (Configuration file)"
        echo "- requirements.txt (Python dependencies)"
        echo ""
        echo "## Backup Info"
        echo "Hostname: $(hostname)"
        echo "User: $(whoami)"
        echo "Working Directory: $PROJECT_DIR"
        echo ""
        echo "## Files Included"
        tar -tzf "$BACKUP_PATH.tar.gz" | head -20
        echo "... (and more)"
        echo ""
        echo "## Restoration Instructions"
        echo "To restore this backup, use:"
        echo "  ./scripts/restore_knowledge_base.sh $BACKUP_PATH.tar.gz"
        echo ""
        echo "Or manually:"
        echo "  tar -xzf $BACKUP_PATH.tar.gz -C /path/to/project"
    } > "$MANIFEST_FILE"

    log_info "Manifest created: $MANIFEST_FILE"
}

cleanup_old_backups() {
    log_info "Cleaning up backups older than $RETENTION_DAYS days..."

    if [[ ! -d "$BACKUP_DIR" ]]; then
        log_warn "Backup directory does not exist"
        return 0
    fi

    DELETED_COUNT=0
    while IFS= read -r -d '' file; do
        log_warn "Deleting old backup: $file"
        rm -f "$file" "${file%.tar.gz}.manifest" 2>/dev/null || true
        ((DELETED_COUNT++))
    done < <(find "$BACKUP_DIR" -name "automata_backup_*.tar.gz" -mtime +$RETENTION_DAYS -print0)

    if [[ $DELETED_COUNT -gt 0 ]]; then
        log_info "Deleted $DELETED_COUNT old backup(s)"
    fi
}

print_summary() {
    local size=$(du -h "$BACKUP_PATH.tar.gz" | cut -f1)

    echo ""
    echo "========================================"
    echo "Backup Summary"
    echo "========================================"
    echo "Status: SUCCESS"
    echo "Backup Name: $BACKUP_NAME"
    echo "Location: $BACKUP_PATH.tar.gz"
    echo "Size: $size"
    echo "Timestamp: $TIMESTAMP"
    echo "Manifest: $BACKUP_PATH.manifest"
    echo "========================================"
    echo ""
    echo "Next Steps:"
    echo "1. Consider moving backup to remote storage"
    echo "2. Store manifest in a safe location"
    echo "3. Test restoration on a test system"
    echo "4. Document backup location and retention policy"
    echo ""
}

###############################################################################
# Main execution
###############################################################################

main() {
    log_info "Starting Project Automata backup process"
    log_info "Backup Directory: $BACKUP_DIR"
    log_info "Retention Period: $RETENTION_DAYS days"
    echo ""

    check_prerequisites || exit 1
    create_backup_dir || exit 1
    create_backup_archive || exit 1
    verify_backup || exit 1
    create_manifest || exit 1
    cleanup_old_backups || exit 1

    print_summary
    log_info "Backup completed successfully"
}

# Run main function
main "$@"
