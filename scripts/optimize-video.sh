#!/usr/bin/env bash
# Video pipeline: assets-src/video/<name>.(mov|mp4|mkv)
#   -> public/media/<name>.mp4  (H.264, faststart, no audio, max 1280px wide)
#   -> public/media/<name>.webm (VP9, no audio)
#   -> assets-src/images/<name>-poster.jpg (first frame; run `npm run assets` after)
# Requires ffmpeg (brew install ffmpeg / winget install ffmpeg).
#
# Usage: npm run assets:video            (all files)
#        bash scripts/optimize-video.sh 01-k2o-teaser
set -euo pipefail

SRC=assets-src/video
OUT=public/media
mkdir -p "$OUT" assets-src/images

shopt -s nullglob
files=("$SRC"/*.{mov,mp4,mkv,MOV,MP4})
[[ $# -gt 0 ]] && files=("$SRC/$1".*)
[[ ${#files[@]} -eq 0 ]] && { echo "No videos in $SRC/"; exit 0; }

for f in "${files[@]}"; do
  name=$(basename "${f%.*}")
  echo "→ $name"
  scale="scale='min(1280,iw)':-2"
  ffmpeg -y -loglevel error -i "$f" -an -vf "$scale,fps=30" \
    -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p -movflags +faststart "$OUT/$name.mp4"
  ffmpeg -y -loglevel error -i "$f" -an -vf "$scale,fps=30" \
    -c:v libvpx-vp9 -b:v 0 -crf 38 -row-mt 1 "$OUT/$name.webm"
  ffmpeg -y -loglevel error -i "$f" -vframes 1 -q:v 2 "assets-src/images/$name-poster.jpg"
  ls -lh "$OUT/$name.mp4" "$OUT/$name.webm" | awk '{print "  " $5 "  " $9}'
done
echo "Done. Run 'npm run assets' to build the poster images."
