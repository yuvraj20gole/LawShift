#!/bin/bash
set -uo pipefail
TERMS="/Users/yuvrajgole/.cursor/projects/Users-yuvrajgole-Documents-NLP-Project/terminals"

KEEP=$(lsof -nP -iTCP:3000,8000,11434 -sTCP:LISTEN -t 2>/dev/null | tr '\n' ' ')
echo "KEEP_LISTEN_PIDS: $KEEP"

should_keep_cmd() {
  local cmd="$1"
  case "$cmd" in
    *ollama*serve*|*"ollama serve"*) return 0 ;;
    *uvicorn*app.main*) return 0 ;;
    *npm*run*dev*|*next*dev*) return 0 ;;
    *next-server*) return 0 ;;
  esac
  return 1
}

is_kill_cmd() {
  local cmd="$1"
  case "$cmd" in
    *inspect_court_s3*|*py_compile*|*boto3*|*rulings_index.json*|*PROCESS_LOG*|*git\ commit*|*git\ commit-tree*|*commit --amend*|*find\ data*|*head\ -n\ *terminals*|*cmp\ -s\ PROCESS_LOG*)
      return 0 ;;
  esac
  # meta cleanup / diagnostic one-liners from agent
  case "$cmd" in
    *Kill\ hung\ agent*|*hung\ agent-ish*|*listeners\ ===*)
      return 0 ;;
  esac
  return 1
}

KILLED=""
for f in "$TERMS"/*.txt; do
  pid=$(awk '/^pid:/{print $2; exit}' "$f")
  [[ -z "${pid:-}" ]] && continue
  # user interactive shells (no command: in metadata)
  if echo " $KEEP " | grep -q " $pid "; then
    continue
  fi
  kill -0 "$pid" 2>/dev/null || continue
  meta_cmd=$(awk '/^command:/{sub(/^command: /,""); print; exit}' "$f" | sed 's/^"//;s/"$//')
  ps_cmd=$(ps -p "$pid" -o command= 2>/dev/null || true)
  cmd="${meta_cmd:-$ps_cmd}"
  if should_keep_cmd "$cmd" || should_keep_cmd "$ps_cmd"; then
    continue
  fi
  # skip bare user shells (1.txt / 2.txt style — no command line)
  if [[ -z "$meta_cmd" ]] && [[ "$ps_cmd" == *zsh* || "$ps_cmd" == *bash* ]] && [[ "$ps_cmd" != *python* && "$ps_cmd" != *git* ]]; then
    continue
  fi
  if ! is_kill_cmd "$cmd" && ! is_kill_cmd "$ps_cmd"; then
    # still kill obvious agent wrappers with long heredocs / python -c zlib git objects
    case "$cmd" in
      *python3\ -c*|*cat-file*|*Co-authored-by:\ Cursor*|*echo\ hello\ \&\&\ pwd*) ;;
      *) continue ;;
    esac
  fi
  short=$(echo "$cmd" | head -c 100)
  echo "KILLING pid=$pid :: $short"
  kill -TERM "$pid" 2>/dev/null || true
  KILLED="$KILLED $pid"
done

sleep 1
for pid in $KILLED; do
  kill -0 "$pid" 2>/dev/null && kill -KILL "$pid" 2>/dev/null && echo "SIGKILL $pid"
done

# pkill stragglers (not long build_rulings_index runs)
pkill -f '/tmp/inspect_court_s3.py' 2>/dev/null && echo "pkill inspect_court_s3" || true
pkill -f 'python -m py_compile scripts/build_rulings_index' 2>/dev/null && echo "pkill py_compile build_rulings" || true

echo "=== KILLED PIDS:$KILLED ==="
echo "=== LISTENERS AFTER ==="
lsof -nP -iTCP:3000,8000,11434 -sTCP:LISTEN 2>/dev/null || true
