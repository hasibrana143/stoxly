# Generate self-signed SSL cert for local development
# Requires OpenSSL (choco install openssl or use WSL)

$certsDir = Join-Path $PSScriptRoot ".." "certs"
New-Item -ItemType Directory -Force -Path $certsDir | Out-Null

$certPath = Join-Path $certsDir "cert.pem"
$keyPath = Join-Path $certsDir "key.pem"

# Check if OpenSSL exists
if (Get-Command "openssl" -ErrorAction SilentlyContinue) {
    openssl req -x509 -newkey rsa:4096 -keyout $keyPath -out $certPath -days 365 -nodes -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
    Write-Host "SSL certs generated:"
    Write-Host "  Cert: $certPath"
    Write-Host "  Key:  $keyPath"
    Write-Host ""
    Write-Host "Set these env vars to enable HTTPS:"
    Write-Host "  SSL_CERT_PATH=$certPath"
    Write-Host "  SSL_KEY_PATH=$keyPath"
} else {
    Write-Host "OpenSSL not found. Install it via 'choco install openssl' or use WSL."
}
