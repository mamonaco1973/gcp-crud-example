#!/usr/bin/env bash
set -euo pipefail

echo "NOTE: Destroying web application..."
cd 02-webapp
terraform destroy -auto-approve
cd ..

echo "NOTE: Destroying Cloud Function and infrastructure..."
cd 01-functions
terraform destroy -auto-approve
cd ..

echo "NOTE: Destroy complete."
