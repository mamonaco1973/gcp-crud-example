#!/usr/bin/env bash
set -euo pipefail

# ─── Clear Firestore notes collection ───────────────────────────────────────────
if [ -f credentials.json ]; then
  project_id=$(jq -r '.project_id' credentials.json)
  client_email=$(jq -r '.client_email' credentials.json)
  gcloud auth activate-service-account "${client_email}" --key-file=credentials.json 2>/dev/null
  gcloud config set project "${project_id}" 2>/dev/null

  echo "NOTE: Deleting Firestore notes collection..."
  gcloud firestore bulk-delete \
    --collection-ids=notes \
    --namespace-ids='(default)' \
    --project="${project_id}" \
    --quiet 2>/dev/null \
    || echo "NOTE: No documents to delete or collection already empty."
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
