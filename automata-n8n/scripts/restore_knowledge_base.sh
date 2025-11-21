#!/bin/bash

###############################################################################
# Project Automata: Knowledge Base Restore Script
#
# Usage: ./restore_knowledge_base.sh <backup_file> [target_dir]
#
# Args:
#   backup_file: Path to backup archive (e.g., automata_backup_20251120_120000.tar.gz)
#   target_dir: Directory to restore to (default: current directory)
#
# Features:
#   - Restores from timestamped backup archives
#   - Verifies backup integrity before extraction
#   - Preserves directory structure
#   - Creates restoration manifest with details
#   - Provides rollback instructions
#   - Validates restored files
#
# Author: Project Automata
# Version: 1.0.0
# Created: 2025-11-20
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

###############################################################################
# Validation functions
###############################################################################

validate_arguments() {
    if [[ $# -lt 1 ]]; then
        log_error "Missing required arguments"
        echo ""
        echo "Usage: $0 <backup_file> [target_dir]"
        echo ""
        echo "Args:"
        echo "  backup_file: Path to backup archive (required)"
        echo "  target_dir: Directory to restore to (optional, default: current directory)"
        echo ""
        echo "Example:"
        echo "  $0 backups/automata_backup_20251120_120000.tar.gz"
        echo "  $0 backups/automata_backup_20251120_120000.tar.gz /opt/automata"
        exit 1
    fi

    BACKUP_FILE="$1"
    TARGET_DIR="${2:-.}"

    if [[ ! -f "$BACKUP_FILE" ]]; then
        log_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi

    if [[ ! -f "${BACKUP_FILE%.tar.gz}.manifest" ]]; then
        log_warn "Manifest file not found for backup: ${BACKUP_FILE%.tar.gz}.manifest"
    fi
}

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

    log_info "All prerequisites met"
}

###############################################################################
# Restoration functions
###############################################################################

verify_backup_integrity() {
    log_step "Verifying backup integrity..."

    if tar -tzf "$BACKUP_FILE" > /dev/null 2>&1; then
        log_info "Backup integrity verified"
        return 0
    else
        log_error "Backup integrity verification failed"
        log_error "The backup file appears to be corrupted"
        exit 1
    fi
}

list_backup_contents() {
    log_step "Listing backup contents..."
    echo ""
    log_info "Backup contents:"
    tar -tzf "$BACKUP_FILE" | head -20
    echo "... (and more)"
    echo ""
}

create_pre_restoration_backup() {
    if [[ -d "$TARGET_DIR/knowledge_base" ]] || [[ -d "$TARGET_DIR/workflows" ]]; then
        log_warn "Existing data found in target directory"
        log_step "Creating pre-restoration backup..."

        PRE_RESTORE_DIR="$TARGET_DIR/.pre_restore_backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$PRE_RESTORE_DIR"

        if [[ -d "$TARGET_DIR/knowledge_base" ]]; then
            cp -r "$TARGET_DIR/knowledge_base" "$PRE_RESTORE_DIR/" || true
        fi

        if [[ -d "$TARGET_DIR/workflows" ]]; then
            cp -r "$TARGET_DIR/workflows" "$PRE_RESTORE_DIR/" || true
        fi

        log_info "Pre-restoration backup created: $PRE_RESTORE_DIR"
    fi
}

restore_backup() {
    log_step "Extracting backup archive..."

    if tar -xzf "$BACKUP_FILE" -C "$TARGET_DIR"; then
        log_info "Backup extracted successfully to $TARGET_DIR"
        return 0
    else
        log_error "Failed to extract backup archive"
        return 1
    fi
}

validate_restoration() {
    log_step "Validating restoration..."

    if [[ -d "$TARGET_DIR/knowledge_base" ]]; then
        KB_FILES=$(find "$TARGET_DIR/knowledge_base" -type f | wc -l)
        log_info "Knowledge base restored with $KB_FILES files"
    fi

    if [[ -d "$TARGET_DIR/workflows" ]]; then
        WF_FILES=$(find "$TARGET_DIR/workflows" -type f | wc -l)
        log_info "Workflows restored with $WF_FILES files"
    fi

    if [[ -f "$TARGET_DIR/config.py" ]]; then
        log_info "Configuration file restored"
    fi

    if [[ -f "$TARGET_DIR/requirements.txt" ]]; then
        log_info "Requirements file restored"
    fi
}

create_restoration_manifest() {
    log_step "Creating restoration manifest..."

    MANIFEST_FILE="$TARGET_DIR/.restoration_manifest_$(date +%Y%m%d_%H%M%S)"

    {
        echo "# Project Automata Restoration Manifest"
        echo "# Created: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo ""
        echo "## Restoration Details"
        echo "Backup File: $BACKUP_FILE"
        echo "Target Directory: $TARGET_DIR"
        echo "Restoration Time: $(date)"
        echo "User: $(whoami)"
        echo "Hostname: $(hostname)"
        echo ""
        echo "## Restored Components"
        [[ -d "$TARGET_DIR/knowledge_base" ]] && echo "✓ knowledge_base/" || echo "✗ knowledge_base/"
        [[ -d "$TARGET_DIR/workflows" ]] && echo "✓ workflows/" || echo "✗ workflows/"
        [[ -d "$TARGET_DIR/logs" ]] && echo "✓ logs/" || echo "✗ logs/"
        [[ -f "$TARGET_DIR/config.py" ]] && echo "✓ config.py" || echo "✗ config.py"
        [[ -f "$TARGET_DIR/requirements.txt" ]] && echo "✓ requirements.txt" || echo "✗ requirements.txt"
        echo ""
        echo "## Rollback Instructions"
        echo "If you need to rollback this restoration:"
        echo ""
        if [[ -n "${PRE_RESTORE_DIR:-}" ]]; then
            echo "Pre-restoration backup available at:"
            echo "  $PRE_RESTORE_DIR"
            echo ""
            echo "To rollback:"
            echo "  rm -rf $TARGET_DIR/knowledge_base $TARGET_DIR/workflows"
            echo "  cp -r $PRE_RESTORE_DIR/* $TARGET_DIR/"
        else
            echo "No pre-restoration backup was created"
            echo "Consider creating a backup before restoring in the future"
        fi
        echo ""
        echo "## Next Steps"
        echo "1. Verify restored data is correct"
        echo "2. Review restored logs for any issues"
        echo "3. Test Project Automata functionality"
        echo "4. Clean up pre-restoration backup if restoration is successful"
        echo ""
        echo "## File Counts"
        echo "Knowledge base files: $(find "$TARGET_DIR/knowledge_base" -type f 2>/dev/null | wc -l)"
        echo "Workflow files: $(find "$TARGET_DIR/workflows" -type f 2>/dev/null | wc -l)"
        echo "Log files: $(find "$TARGET_DIR/logs" -type f 2>/dev/null | wc -l)"
    } > "$MANIFEST_FILE"

    log_info "Restoration manifest created: $MANIFEST_FILE"
}

print_summary() {
    echo ""
    echo "========================================"
    echo "Restoration Summary"
    echo "========================================"
    echo "Status: SUCCESS"
    echo "Backup File: $BACKUP_FILE"
    echo "Target Directory: $TARGET_DIR"
    echo "Restored At: $(date)"
    echo "========================================"
    echo ""
    echo "Next Steps:"
    echo "1. Verify restored data is correct"
    echo "2. Test Project Automata functionality"
    echo "3. If satisfied with restoration, delete:"
    if [[ -n "${PRE_RESTORE_DIR:-}" ]]; then
        echo "   rm -rf $PRE_RESTORE_DIR"
    fi
    echo ""
}

###############################################################################
# Main execution
###############################################################################

main() {
    validate_arguments "$@"

    log_info "Starting Project Automata restoration process"
    log_info "Backup File: $BACKUP_FILE"
    log_info "Target Directory: $TARGET_DIR"
    echo ""

    check_prerequisites
    verify_backup_integrity
    list_backup_contents
    create_pre_restoration_backup
    restore_backup || exit 1
    validate_restoration
    create_restoration_manifest

    print_summary
    log_info "Restoration completed successfully"
}

# Run main function
main "$@"
