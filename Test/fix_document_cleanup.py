#!/usr/bin/env python3
"""
Патч для исправления полной очистки данных при удалении документа.
Добавляет:
1. Удаление файлов чанков из MinIO/S3
2. Очистку кеша парсера
3. Проверку полноты удаления из multivector store
"""

import asyncio
import logging
from typing import Optional
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class EnhancedDocumentCleanup:
    """Улучшенная очистка документов с полным удалением всех связанных данных"""
    
    def __init__(self, storage_client, endpoint_url: str):
        self.s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id='minioadmin',
            aws_secret_access_key='minioadmin'
        )
    
    async def cleanup_multivector_chunks(self, document_id: str, bucket: str = "morphik-storage"):
        """
        Удаляет все файлы чанков из MinIO для данного документа
        
        Args:
            document_id: ID документа
            bucket: Имя bucket в MinIO
        """
        prefix = f"multivector-chunks/multivector-chunks/morphik_app/{document_id}/"
        
        try:
            # Список всех объектов с префиксом документа
            response = self.s3.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                logger.info(f"No chunks found for document {document_id}")
                return
            
            # Удаляем все найденные файлы
            objects_to_delete = []
            for obj in response['Contents']:
                objects_to_delete.append({'Key': obj['Key']})
                logger.debug(f"Marking for deletion: {obj['Key']}")
            
            if objects_to_delete:
                delete_response = self.s3.delete_objects(
                    Bucket=bucket,
                    Delete={'Objects': objects_to_delete}
                )
                
                deleted_count = len(delete_response.get('Deleted', []))
                logger.info(f"Deleted {deleted_count} chunk files for document {document_id}")
                
                # Проверяем ошибки
                if 'Errors' in delete_response:
                    for error in delete_response['Errors']:
                        logger.error(f"Failed to delete {error['Key']}: {error['Message']}")
            
        except ClientError as e:
            logger.error(f"Error cleaning up chunks for document {document_id}: {e}")
            raise
    
    async def cleanup_parser_cache(self):
        """
        Очищает кеш парсера между документами
        """
        # Очистка глобального кеша unstructured
        try:
            from unstructured.partition.auto import partition
            # Сброс внутреннего кеша если он существует
            if hasattr(partition, '_cache'):
                partition._cache.clear()
                logger.info("Cleared unstructured parser cache")
        except Exception as e:
            logger.debug(f"Could not clear parser cache: {e}")
    
    async def verify_complete_deletion(self, document_id: str, db_connection):
        """
        Проверяет полноту удаления документа из всех хранилищ
        
        Returns:
            dict: Статус удаления из каждого хранилища
        """
        status = {
            'pgvector': False,
            'multivector': False,
            'minio': False,
            'database': False
        }
        
        try:
            # Проверка pgvector
            cursor = db_connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM vector_embeddings WHERE document_id = %s",
                (document_id,)
            )
            count = cursor.fetchone()[0]
            status['pgvector'] = (count == 0)
            if count > 0:
                logger.warning(f"Found {count} remaining chunks in pgvector for document {document_id}")
            
            # Проверка multivector store
            cursor.execute(
                "SELECT COUNT(*) FROM multivector_chunks WHERE document_id = %s",
                (document_id,)
            )
            count = cursor.fetchone()[0]
            status['multivector'] = (count == 0)
            if count > 0:
                logger.warning(f"Found {count} remaining chunks in multivector for document {document_id}")
            
            # Проверка MinIO
            prefix = f"multivector-chunks/multivector-chunks/morphik_app/{document_id}/"
            response = self.s3.list_objects_v2(
                Bucket="morphik-storage",
                Prefix=prefix,
                MaxKeys=1
            )
            status['minio'] = ('Contents' not in response)
            if not status['minio']:
                logger.warning(f"Found remaining files in MinIO for document {document_id}")
            
            # Проверка основной БД
            cursor.execute(
                "SELECT COUNT(*) FROM documents WHERE external_id = %s",
                (document_id,)
            )
            count = cursor.fetchone()[0]
            status['database'] = (count == 0)
            
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error verifying deletion for document {document_id}: {e}")
        
        return status


async def enhanced_delete_document(document_service, document_id: str, auth):
    """
    Улучшенное удаление документа с полной очисткой
    
    Этот метод заменяет стандартный delete_document для обеспечения
    полной очистки всех связанных данных
    """
    logger.info(f"Starting enhanced deletion for document {document_id}")
    
    # Создаем помощник для очистки
    cleanup = EnhancedDocumentCleanup(
        document_service.storage,
        endpoint_url="http://135.181.106.12:32000"
    )
    
    # 1. Стандартное удаление через document_service
    result = await document_service.delete_document(document_id, auth)
    
    if not result:
        logger.error(f"Standard deletion failed for document {document_id}")
        return False
    
    # 2. Дополнительная очистка чанков из MinIO
    await cleanup.cleanup_multivector_chunks(document_id)
    
    # 3. Очистка кеша парсера
    await cleanup.cleanup_parser_cache()
    
    # 4. Проверка полноты удаления (опционально)
    # status = await cleanup.verify_complete_deletion(document_id, db_connection)
    # logger.info(f"Deletion verification status: {status}")
    
    logger.info(f"Enhanced deletion completed for document {document_id}")
    return True


if __name__ == "__main__":
    # Тестовое удаление
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python fix_document_cleanup.py <document_id>")
        sys.exit(1)
    
    document_id = sys.argv[1]
    
    async def test_cleanup():
        cleanup = EnhancedDocumentCleanup(
            None,
            endpoint_url="http://135.181.106.12:32000"
        )
        await cleanup.cleanup_multivector_chunks(document_id)
        print(f"Cleaned up chunks for document {document_id}")
    
    asyncio.run(test_cleanup())