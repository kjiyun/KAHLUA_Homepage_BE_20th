from django.shortcuts import render
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from rest_framework import viewsets, status

from kahluaproject.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

import boto3


def image_view(request, image_name):
    storage = S3Boto3Storage()
    file = storage.open(image_name)
    
    return Response({
            'data': file
        },status=status.HTTP_200_OK)


class ImageUploadView(viewsets.ModelViewSet):
    permission_classes = (AllowAny, )

    @swagger_auto_schema(
        operation_id='presigned url 제공',
        operation_description='''
            s3에서 받아온 presigned url을 알려줍니다.
        ''',
        request_body=openapi.Schema(
            'presigned url 제공',
            type=openapi.TYPE_OBJECT,
            properties={
                'file_name': openapi.Schema('file_name', type=openapi.TYPE_STRING),
            }
        ),
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json": {
                        "status": "success",
                        "data": "https://kahlua-bucket.s3/"
                    }
                }
            )
        }
    )
    def generate_presigned_url(self, request):
        if request.method == 'POST':
            file_name = request.POST.get('file_name')

            if file_name:
                # AWS S3 클라이언트 생성
                s3_client = boto3.client('s3',
                                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                                
                try:
                    presigned_url = s3_client.generate_presigned_url('put_object',
                                                                     Params={'Bucket': AWS_STORAGE_BUCKET_NAME,
                                                                             'Key': file_name},
                                                                     ExpiresIn=3600)  # url 만료시간
                except Exception as e:
                    return Response({
                        'error': str(e),
                    },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                return Response({
                    'status': 'success',
                    'presigned_url': presigned_url
                }, status=status.HTTP_200_OK)
            
        return Response({
            'error':'Invalid request',
        }, status=status.HTTP_400_BAD_REQUEST)