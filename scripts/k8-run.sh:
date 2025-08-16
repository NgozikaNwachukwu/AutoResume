#!/usr/bin/env bash
set -euo pipefail

NS=autoresume
OUT_LOCAL="${1:-AutoResume.fromKIND.pdf}"

echo "→ Ensuring kind cluster is reachable…"
kubectl version --client >/dev/null
kubectl config current-context >/dev/null || { echo "kubectl has no current context"; exit 1; }

echo "→ Create namespace & ConfigMap (from repo sample_data)"
kubectl get ns "$NS" >/dev/null 2>&1 || kubectl create ns "$NS"
kubectl -n "$NS" create configmap autoresume-sample \
  --from-file=minimal.json=sample_data/minimal.json \
  -o yaml --dry-run=client | kubectl apply -f -

echo "→ (Re)create Job that sleeps after writing PDF so we can copy it"
kubectl -n "$NS" delete job autoresume-generate-pdf 2>/dev/null || true
kubectl apply -f - <<'YAML'
apiVersion: batch/v1
kind: Job
metadata:
  name: autoresume-generate-pdf
  namespace: autoresume
spec:
  backoffLimit: 0
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: autoresume
          image: ghcr.io/ngozikanwachukwu/autoresume:main
          imagePullPolicy: Always
          workingDir: /app
          command:
            - /bin/sh
            - -lc
            - >
              python -m src.cli --input /in/minimal.json --output /out/AutoResume.pdf
              && echo "PDF written; sleeping for copy…"
              && sleep 600
          volumeMounts:
            - name: input
              mountPath: /in
              readOnly: true
            - name: output
              mountPath: /out
      volumes:
        - name: input
          configMap:
            name: autoresume-sample
            items:
              - key: minimal.json
                path: minimal.json
        - name: output
          emptyDir: {}
YAML

echo "→ Waiting for pod to be Running…"
POD=""
until POD=$(kubectl -n "$NS" get pods -l job-name=autoresume-generate-pdf -o jsonpath='{.items[0].metadata.name}' 2>/dev/null) && \
      PHASE=$(kubectl -n "$NS" get pod "$POD" -o jsonpath='{.status.phase}') && \
      [ "$PHASE" = "Running" ]; do
  printf "."
  sleep 1
done
echo -e "\n→ Copying /out/AutoResume.pdf → $OUT_LOCAL"
kubectl -n "$NS" cp "$POD:/out/AutoResume.pdf" "$OUT_LOCAL"

echo "→ Cleaning up Job"
kubectl -n "$NS" delete job autoresume-generate-pdf --wait=true >/dev/null

echo "Wrote $OUT_LOCAL"
