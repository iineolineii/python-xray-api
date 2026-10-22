#!/usr/bin/env bash
set -euo pipefail

STATUS_OUTPUT="${1:-/dev/stdout}"
RESULT_OUTPUT="${2:-/dev/null}"

error() {
    echo "❌ ERROR: $*" >&2
    exit 1
}

UPSTREAM_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

if [ -z "$UPSTREAM_VERSION" ]; then
    error "Failed to fetch upstream version (no tags found)"
fi

XRAY_VERSION=$(git ls-remote --tags --refs https://github.com/XTLS/Xray-core.git | grep -oP 'refs/tags/v\K[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -n1)

if [ -z "$XRAY_VERSION" ]; then
    error "Failed to fetch Xray-core version"
fi

# Split upstream version assuming format "v${FEATURE_VERSION}+${XRAY_VERSION}"
FEATURE_VERSION=$(echo "$UPSTREAM_VERSION" | cut -d'+' -f1 | sed 's/^v//')
PREVIOUS_XRAY_VERSION=$(echo "$UPSTREAM_VERSION" | cut -d'+' -f2)

# Check if update is needed (ИСПРАВЛЕНО: используем XRAY_VERSION)
if [ "$XRAY_VERSION" != "$PREVIOUS_XRAY_VERSION" ]; then
    NEEDS_UPDATE="true"
    STATUS_MESSAGE="🔄 Updating..."
else
    NEEDS_UPDATE="false"
    STATUS_MESSAGE="✅ Update is not needed"
fi

# Write summary info to STATUS_OUTPUT (e.g., $GITHUB_STEP_SUMMARY)
{
    echo "Feature version:            ${FEATURE_VERSION}"
    echo "Previous Xray-core version: ${PREVIOUS_XRAY_VERSION}"
    echo "Latest Xray-core version:   ${XRAY_VERSION}"
    echo ""
    echo "## ${STATUS_MESSAGE}"
} >> "$STATUS_OUTPUT"

# Write results to RESULT_OUTPUT (e.g., $GITHUB_OUTPUT)
{
    echo "feature_version=${FEATURE_VERSION}"
    echo "previous_xray_version=${PREVIOUS_XRAY_VERSION}"
    echo "latest_xray_version=${XRAY_VERSION}"
    echo "needs_update=${NEEDS_UPDATE}"
    echo "new_version=${FEATURE_VERSION}+${XRAY_VERSION}"
} >> "$RESULT_OUTPUT"
