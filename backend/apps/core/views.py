"""
Core views for file uploads and utilities.
"""
import logging
import boto3
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


class S3PresignedURLViewSet(viewsets.ViewSet):
    """
    ViewSet for generating presigned S3 URLs for direct uploads.
    Supports direct browser-to-S3 uploads bypassing Django.
    """
    
    def get_permissions(self):
        """Admin-only for presigned URLs to control upload access."""
        if self.action in ['get_upload_url', 'get_product_upload_url']:
            return [IsAdminUser()]
        return [AllowAny()]
    
    @action(detail=False, methods=['post'])
    def get_upload_url(self, request):
        """
        Generate a presigned URL for direct S3 upload.
        
        Expected payload:
        {
            "filename": "my-file.jpg",
            "file_type": "image/jpeg",
            "folder": "media/uploads"  # optional, defaults to "media/uploads"
        }
        
        Returns:
        {
            "upload_url": "https://...",
            "file_key": "media/uploads/my-file.jpg"
        }
        """
        if not settings.USE_S3:
            return Response(
                {'error': 'S3 is not configured. Set USE_S3=True in environment.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        filename = request.data.get('filename', '').strip()
        file_type = request.data.get('file_type', 'application/octet-stream').strip()
        folder = request.data.get('folder', 'media/uploads').strip()
        
        if not filename:
            raise ValidationError({'filename': 'Filename is required.'})
        
        # Sanitize filename
        filename = self._sanitize_filename(filename)
        
        # Build S3 key
        file_key = f"{folder}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        
        try:
            presigned_url = self._generate_presigned_url(file_key, file_type)
            return Response({
                'upload_url': presigned_url,
                'file_key': file_key,
                'bucket': settings.AWS_STORAGE_BUCKET_NAME,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Failed to generate presigned URL")
            return Response(
                {'error': 'Failed to generate upload URL.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def get_product_upload_url(self, request):
        """
        Generate presigned URL for product image upload.
        Folder automatically set to 'media/products'.
        """
        request.data._mutable = True  # Allow modification of request.data
        request.data['folder'] = 'media/products'
        return self.get_upload_url(request)
    
    def _sanitize_filename(self, filename):
        """Remove unsafe characters from filename."""
        import re
        # Keep alphanumeric, dots, hyphens, underscores
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        return safe_name[:100]  # Limit length
    
    def _generate_presigned_url(self, file_key, file_type, expiration=3600):
        """
        Generate AWS presigned URL for direct S3 upload.
        
        Args:
            file_key: S3 object key (path in bucket)
            file_type: MIME type (Content-Type)
            expiration: URL expiration in seconds (default 1 hour)
        
        Returns:
            Presigned URL string
        """
        s3_client = boto3.client(
            's3',
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': file_key,
                'ContentType': file_type,
                'ACL': getattr(settings, 'AWS_DEFAULT_ACL', 'public-read'),
            },
            ExpiresIn=expiration,
        )
        
        return presigned_url
