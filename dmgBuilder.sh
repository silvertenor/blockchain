#!/bin/sh
# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/GEthereum.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/GEthereum.dmg" && rm "dist/GEthereum.dmg"
create-dmg \
  --volname "app" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --hide-extension "GEthereum.app" \
  --app-drop-link 425 120 \
  "dist/GEthereum.dmg" \
  "dist/dmg/"