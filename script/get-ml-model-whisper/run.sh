#!/bin/bash

set -e

# Default checkpoint path
CHECKPOINT_PATH=${MLC_ML_MODEL_WHISPER_PATH:-whisper-large-v3}

git lfs install

if [ ! -d "$CHECKPOINT_PATH" ]; then
  git clone https://huggingface.co/openai/whisper-large-v3 "$CHECKPOINT_PATH"
fi

cd "${CHECKPOINT_PATH}"
git checkout 06f233fe06e710322aca913c1bc4249a0d71fce1
