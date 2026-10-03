param(
    [string]$Message = "Update Quantum Qubits project"
)

Write-Host "Checking project changes..."

git status --short

if (-not (git status --porcelain)) {
    Write-Host "No changes found. Nothing to upload."
    exit
}

git add .

git commit -m "$Message"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Commit failed. Push cancelled."
    exit 1
}

git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully updated GitHub."
    Write-Host "Render will automatically deploy the new commit."
} else {
    Write-Host "GitHub push failed."
}