#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 2 ]]; then
  echo 'Usage: bash scripts/upload-pdfs.sh SOURCE_DIRECTORY s3://BUCKET[/PREFIX] [--apply] [AWS CLI options...]' >&2
  exit 1
fi
source_dir="$1"
destination="$2"
shift 2
mode=(--dryrun)
if [[ "${1:-}" == '--apply' ]]; then
  mode=()
  shift
fi
aws s3 sync "$source_dir" "$destination" --exclude '*' --include '*.pdf' --include '*.PDF' \
  --content-type application/pdf --cache-control 'public,max-age=86400' "${mode[@]}" "$@"
