# Test all department admin logins
$emails = @(
    "public.works@cirp.com",
    "water.&.sewage@cirp.com", 
    "sanitation@cirp.com",
    "electrical.services@cirp.com"
)

$password = "Test@123"

Write-Host "`n🔐 Testing Department Admin Logins...`n" -ForegroundColor Cyan

foreach ($email in $emails) {
    Write-Host "Testing: $email" -ForegroundColor Yellow
    
    $body = @{
        email = $email
        password = $password
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod -Uri "http://localhost:3002/api/auth/login/" `
            -Method POST `
            -ContentType "application/json" `
            -Body $body `
            -ErrorAction Stop
        
        Write-Host "✅ SUCCESS - Token: $($response.token.Substring(0,20))..." -ForegroundColor Green
        Write-Host "   Name: $($response.user.full_name)" -ForegroundColor Gray
        Write-Host "   Role: $($response.user.role)`n" -ForegroundColor Gray
    }
    catch {
        Write-Host "❌ FAILED - $($_.Exception.Message)`n" -ForegroundColor Red
    }
}
