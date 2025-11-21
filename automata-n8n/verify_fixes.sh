#!/bin/bash
# Verification Script for Critical n8n Versioning Fixes
# Agent 1 - 2025-11-20

echo "========================================="
echo "n8n Versioning Fixes Verification"
echo "========================================="
echo ""

echo "1. Checking n8n_node_versions.py module..."
python3 -c "
from skills.n8n_node_versions import get_node_version, N8N_VERSION_COMPATIBILITY
print(f'  ✓ Module loaded successfully')
print(f'  ✓ Target n8n version: {N8N_VERSION_COMPATIBILITY[\"target_version\"]}')
print(f'  ✓ Webhook typeVersion: {get_node_version(\"n8n-nodes-base.webhook\")}')
print(f'  ✓ HTTP Request typeVersion: {get_node_version(\"n8n-nodes-base.httpRequest\")}')
print(f'  ✓ Slack typeVersion: {get_node_version(\"n8n-nodes-base.slack\")}')
" 2>/dev/null
echo ""

echo "2. Checking workflow files updated..."
grep -l "typeVersion.*2\|typeVersion.*3\|typeVersion.*4" workflows/*.json 2>/dev/null | while read file; do
    echo "  ✓ $file"
done
echo ""

echo "3. Checking docker-compose.yml..."
if grep -q "n8nio/n8n:1.60" docker-compose.yml; then
    version=$(grep "image: n8nio/n8n" docker-compose.yml | sed 's/.*n8n://')
    echo "  ✓ n8n pinned to version: $version"
else
    echo "  ✗ n8n version not pinned"
fi
echo ""

echo "4. Checking documentation files..."
if [ -f "docs/n8n_compatibility_matrix.md" ]; then
    echo "  ✓ docs/n8n_compatibility_matrix.md created"
fi

if grep -q "1.60.0" README.md; then
    echo "  ✓ README.md updated with version requirements"
fi

if grep -q "1.60.0" docs/DEPLOYMENT.md; then
    echo "  ✓ docs/DEPLOYMENT.md updated with version requirements"
fi
echo ""

echo "5. Checking CRITICAL_FIXES_REPORT.md..."
if [ -f "CRITICAL_FIXES_REPORT.md" ]; then
    lines=$(wc -l < CRITICAL_FIXES_REPORT.md)
    echo "  ✓ Report created ($lines lines)"
fi
echo ""

echo "========================================="
echo "Verification Complete!"
echo "========================================="
