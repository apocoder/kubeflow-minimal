# Kubernetes ortamında Kubeflow (AI) Pipelines (KFP v2) Kurulumu

Minimal bir örnek: **Terraform → GKE (VPC-native) → Kubeflow Pipelines Standalone (KFP v2)**.

## Klasör Yapısı
```
kubeflow-minimal/
├─ infra/                 # Terraform ile GKE kurulumu
├─ scripts/               # KFP kurulumu
└─ pipelines/             # Örnek KFP v2 pipeline
```

## Ön Koşullar
- Google Cloud projesi (faturalama bağlı)
- CLI: `gcloud`, `kubectl`, `terraform (>=1.6)`
- Yerel Python 3.10+ (pipeline derlemek için)

---

## 1) GKE'yi Terraform ile kurun

```bash
cd infra
export TF_VAR_project_id="YOUR_GCP_PROJECT_ID"
terraform init
terraform apply -auto-approve
```

Kubeconfig almak için (Terraform çıktısından otomatik gelir):
```bash
terraform output -raw get_credentials_cmd
# Komut çıktısını kopyala çalıştır (örnek):
# gcloud container clusters get-credentials kubeflow-min --region europe-west3 --project YOUR_GCP_PROJECT_ID
```

Doğrula:
```bash
kubectl get nodes
```

---

## 2) Kubeflow Pipelines (Standalone) kurun

```bash
cd ..
chmod +x scripts/install_kfp.sh
./scripts/install_kfp.sh
```

UI'ya erişim (port-forward):
```bash
kubectl -n kubeflow port-forward svc/ml-pipeline-ui 8080:80
# Tarayıcı: http://localhost:8080
```

---



## Temizlik
```bash
# Port-forward varsa Ctrl+C
cd infra
terraform destroy -auto-approve
```

## Notlar
- Bu kurulum **minimal** ve **auth yok** (port-forward ile erişim). Üretimde Ingress + HTTPS + IAP/OIDC önerilir.
- Node pool **preemptible** (spot) ve 1–3 autoscale ayarlı, düşük maliyet içindir.
- Pipeline bileşenleri `pip install` yapar; üretimde custom container imajlarını tercih edin.
