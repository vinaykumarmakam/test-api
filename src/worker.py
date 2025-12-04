"""
Background worker for data processing
Uses Celery for distributed task queue
"""
from celery import Celery
import logging
from typing import Dict, Any
import boto3
from redis import Redis
import json

from .config import settings

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Initialize connections
redis_client = Redis.from_url(settings.REDIS_URL)
s3_client = boto3.client(
    's3',
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY
)

def process_data_task(job_id: str, data: Dict[str, Any], priority: str = "normal"):
    """
    Background task for data processing
    Can be called directly or via Celery
    """
    try:
        logger.info(f"Processing job {job_id} with priority {priority}")
        
        # Update job status in Redis
        redis_client.hset(
            f"job:{job_id}",
            mapping={
                "status": "processing",
                "progress": "0.0",
                "started_at": str(json.dumps(data))
            }
        )
        
        # Process data (placeholder - implement your logic)
        result = {
            "processed": True,
            "input_size": len(str(data)),
            "job_id": job_id
        }
        
        # Store result in MinIO
        s3_client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=f"results/{job_id}.json",
            Body=json.dumps(result)
        )
        
        # Update job status
        redis_client.hset(
            f"job:{job_id}",
            mapping={
                "status": "completed",
                "progress": "1.0",
                "result_path": f"results/{job_id}.json"
            }
        )
        
        logger.info(f"Completed job {job_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        redis_client.hset(
            f"job:{job_id}",
            mapping={
                "status": "failed",
                "error": str(e)
            }
        )
        raise

@celery_app.task(name="process_data")
def process_data_celery(job_id: str, data: Dict[str, Any], priority: str = "normal"):
    """Celery task wrapper"""
    return process_data_task(job_id, data, priority)
