$body = @{
    title = "测试需求提交功能"
    description = "这是一个测试需求，测试局域网内提交需求是否能正常通知到管理员。"
    contact = "test@test.com"
    priority = "normal"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri http://localhost:8000/api/request -Method Post -Body $body -ContentType "application/json"

Write-Host "响应结果:"
Write-Host $response
