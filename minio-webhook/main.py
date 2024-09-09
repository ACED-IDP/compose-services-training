from logging.config import dictConfig
import logging
from config import LogConfig

from fastapi import FastAPI

# https://docs.aws.amazon.com/AmazonS3/latest/userguide/notification-content-structure.html
# https://pydantic-docs.helpmanual.io/datamodel_code_generator/
from model import Model

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Health OK."}


@app.head("/file-uploaded")
async def uploaded_head():
    """Receive HEAD from minio server when minio starts."""
    pass


@app.post("/file-uploaded")
async def uploaded(body: Model):
    """Receive POST from minio server when file uploaded."""
    if body.EventName != 's3:ObjectCreated:Put':
        logger.warning(f"Ignoring unexpected event type {body}")
        return
    # logger.info(f"Processing event type {body.EventName} {body}")
    for record in body.Records:
        logger.info(
            f"Update gen3 sheepdog and indexd with: {record.s3.bucket.name} {record.s3.object.key} {record.s3.object.size} {record.s3.object.eTag} {record.s3.object.userMetadata}")
    return

# https://aced-training.compbio.ohsu.edu/index/index?acl=null&uploader=test&start=00000000-0000-0000-0000-000000000000&limit=1024


# setup logging
dictConfig(LogConfig().dict())
logger = logging.getLogger("minio-webhook")

