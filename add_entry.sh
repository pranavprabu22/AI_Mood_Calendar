#!/bin/bash

# Usage: ./add_entry.sh USER_ID MOOD EMOTION NOTE
USER_ID=$1
MOOD=$2
EMOTION=$3
NOTE=$4

python3 - <<EOF
from mood_logger import add_entry, init_db

init_db()
add_entry("$USER_ID", $MOOD, "$EMOTION", "$NOTE")
print("Added entry for user '$USER_ID' with mood = $MOOD, emotion = '$EMOTION', and note = '$NOTE'")
EOF
