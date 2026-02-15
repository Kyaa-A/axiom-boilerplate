#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
API_PREFIX="${API_PREFIX:-/api/v1}"
STRICT_AI="${STRICT_AI:-0}"
AUTH_TOKEN="${AUTH_TOKEN:-}"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

echo "Running smoke test against ${BASE_URL}${API_PREFIX}"

AUTH_ARGS=()
if [[ -n "${AUTH_TOKEN}" ]]; then
  AUTH_ARGS=(-H "Authorization: Bearer ${AUTH_TOKEN}")
fi

health_code="$(curl -sS -o "${TMP_DIR}/health.json" -w '%{http_code}' "${BASE_URL}/health")"
if [[ "${health_code}" != "200" ]]; then
  echo "Health check failed (${health_code})"
  cat "${TMP_DIR}/health.json"
  exit 1
fi
echo "Health check: OK"

if [[ -n "${AUTH_TOKEN}" ]]; then
  auth_me_code="$(curl -sS -o "${TMP_DIR}/auth_me.json" -w '%{http_code}' \
    "${AUTH_ARGS[@]}" \
    "${BASE_URL}${API_PREFIX}/auth/me")"

  if [[ "${auth_me_code}" != "200" ]]; then
    echo "Auth check failed (${auth_me_code})"
    cat "${TMP_DIR}/auth_me.json"
    exit 1
  fi
  echo "Auth check: OK"
fi

cat > "${TMP_DIR}/document.json" <<EOF
{
  "title": "Smoke Test Document",
  "content": "Axiom boilerplate uses Weaviate for vector search and retrieval.",
  "source": "infra/scripts/smoke-test.sh"
}
EOF

create_code="$(curl -sS -o "${TMP_DIR}/create.json" -w '%{http_code}' \
  -X POST "${BASE_URL}${API_PREFIX}/documents/" \
  "${AUTH_ARGS[@]}" \
  -H "Content-Type: application/json" \
  --data-binary "@${TMP_DIR}/document.json")"

if [[ "${create_code}" == "201" ]]; then
  document_id="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["id"])' "${TMP_DIR}/create.json")"
  echo "Document create: OK (id=${document_id})"
else
  echo "Document create returned ${create_code}"
  cat "${TMP_DIR}/create.json"
  echo

  if [[ "${create_code}" == "401" || "${create_code}" == "403" ]]; then
    if [[ -z "${AUTH_TOKEN}" ]]; then
      echo "Protected API flow skipped: set AUTH_TOKEN for auth-required smoke test."
      exit 0
    fi
    echo "Protected API request failed with provided AUTH_TOKEN."
    exit 1
  fi

  if grep -Eqi "api key|authentication|unauthorized|forbidden|invalid" "${TMP_DIR}/create.json"; then
    if [[ "${STRICT_AI}" == "1" ]]; then
      echo "AI provider credentials are invalid or missing (STRICT_AI=1)."
      exit 1
    fi
    echo "AI-dependent flow skipped due missing/invalid API credentials."
    exit 0
  fi

  exit 1
fi

cat > "${TMP_DIR}/query.json" <<EOF
{
  "query": "What vector database does this boilerplate use?",
  "top_k": 3,
  "score_threshold": 0.5
}
EOF

query_code="$(curl -sS -o "${TMP_DIR}/query_result.json" -w '%{http_code}' \
  -X POST "${BASE_URL}${API_PREFIX}/ai/query" \
  "${AUTH_ARGS[@]}" \
  -H "Content-Type: application/json" \
  --data-binary "@${TMP_DIR}/query.json")"

if [[ "${query_code}" != "200" ]]; then
  echo "RAG query failed (${query_code})"
  cat "${TMP_DIR}/query_result.json"
  echo

  if [[ "${query_code}" == "401" || "${query_code}" == "403" ]]; then
    if [[ -z "${AUTH_TOKEN}" ]]; then
      echo "Protected API flow skipped: set AUTH_TOKEN for auth-required smoke test."
      exit 0
    fi
  fi

  exit 1
fi

sources_count="$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1])).get("sources", [])))' "${TMP_DIR}/query_result.json")"
echo "RAG query: OK (sources=${sources_count})"
echo "Smoke test passed."
