# Run this script to migrate your local media files to S3
# Replace YOUR_AWS_KEY and YOUR_AWS_SECRET with your actual credentials

$env:USE_S3="True"
$env:AWS_STORAGE_BUCKET_NAME="pieglobal"
$env:AWS_S3_REGION_NAME="us-east-1"
$env:AWS_ACCESS_KEY_ID="YOUR_AWS_KEY"
$env:AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET"

Write-Host "Testing S3 connection with dry run..." -ForegroundColor Yellow
python manage.py migrate_media_to_s3 --dry-run

Write-Host "`nReady to upload? Press Enter to continue or Ctrl+C to cancel..." -ForegroundColor Cyan
Read-Host

Write-Host "Uploading files to S3..." -ForegroundColor Green
python manage.py migrate_media_to_s3

Write-Host "`nMigration complete! Check your S3 bucket: https://s3.console.aws.amazon.com/s3/buckets/pieglobal" -ForegroundColor Green
