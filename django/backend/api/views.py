import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FileUploadSerializer
from backend.ml_models.predictions import process_and_predict


class FileUploadView(APIView):
    def post(self, request, format=None):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']

            # アップロードされたファイルを一時的に保存
            temp_file_path = os.path.join('/tmp', uploaded_file.name)
            with open(temp_file_path, 'wb+') as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)

            try:
                # ファイルを処理して予測を取得
                predictions = process_and_predict(temp_file_path)

                # 一時ファイルを削除
                os.remove(temp_file_path)

                return Response({'predictions': predictions}, status=status.HTTP_200_OK)
            except Exception as e:
                # エラー処理（必要に応じてログを出力）
                os.remove(temp_file_path)
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

