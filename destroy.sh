#!/usr/bin/env bash
set -euo pipefail

# ─── Clear Firestore notes collection ───────────────────────────────────────────
if [ -f credentials.json ]; then
  project_id=$(jq -r '.project_id' credentials.json)
  client_email=$(jq -r '.client_email' credentials.json)
  gcloud auth activate-service-account "${client_email}" --key-file=credentials.json 2>/dev/null
  gcloud config set project "${project_id}" 2>/dev/null

  echo "NOTE: Deleting Firestore notes collection..."
  COLLECTION="projects/${project_id}/databases/(default)/documents/notes"
  doc_count=0
  while IFS= read -r doc_name; do
    [[ -z "${doc_name}" ]] && continue
    gcloud firestore documents delete "${doc_name}" --quiet
    doc_count=$((doc_count + 1))
  done < <(gcloud firestore documents list "${COLLECTION}" \
    --format="value(name)" --project="${project_id}" 2>/dev/null)
  echo "NOTE: Deleted ${doc_count} document(s) from notes collection."
fi

echo "NOTE: Destroying web application..."
cd 02-webapp
terraform destroy -auto-approve
cd ..

echo "NOTE: Destroying Cloud Function and infrastructure..."
cd 01-functions
terraform destroy -auto-approve
cd ..

echo "NOTE: Destroy complete."
