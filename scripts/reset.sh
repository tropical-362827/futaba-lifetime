#!/bin/bash

# threads.json を "[]" にする
echo "[]" > threads.json
echo "Updated threads.json to contain only []"

# ./log/catalog/* の内容を削除
if [ -d ./log/catalog ]; then
  rm -rf ./log/catalog/*
  echo "Cleared all contents in ./log/catalog/"
else
  echo "Directory ./log/catalog/ does not exist"
fi

# ./log/threads/* の内容を削除
if [ -d ./log/threads ]; then
  rm -rf ./log/threads/*
  echo "Cleared all contents in ./log/threads/"
else
  echo "Directory ./log/threads/ does not exist"
fi

# output.log を空ファイルにする
> output.log
echo "Emptied output.log"

echo "Reset complete!"
