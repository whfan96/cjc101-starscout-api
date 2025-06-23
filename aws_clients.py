import os
from dotenv import load_dotenv
import boto3

# 指定 .env 路徑，確保讀到正確檔案
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
    raise RuntimeError("AWS_ACCESS_KEY and AWS_SECRET_KEY must be set in environment variables or in the .env file")

def create_boto3_client(service_name):
    return boto3.client(
        service_name,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
    )

# 目前已包含的服務 clients
ec2_client = create_boto3_client("ec2")
cloudwatch_client = create_boto3_client("cloudwatch")
cost_explorer_client = create_boto3_client("ce")
apprunner_client = create_boto3_client("apprunner")
logs_client = create_boto3_client("logs")

iam_client = create_boto3_client("iam")
s3_client = create_boto3_client("s3")
sns_client = create_boto3_client("sns")
events_client = create_boto3_client("events")
lambda_client = create_boto3_client("lambda")
config_client = create_boto3_client("config")

# 其他建議加入的服務 clients
dynamodb_client = create_boto3_client("dynamodb")
rds_client = create_boto3_client("rds")
elb_client = create_boto3_client("elbv2")
autoscaling_client = create_boto3_client("autoscaling")
ecs_client = create_boto3_client("ecs")
eks_client = create_boto3_client("eks")
cloudformation_client = create_boto3_client("cloudformation")
secretsmanager_client = create_boto3_client("secretsmanager")
ssm_client = create_boto3_client("ssm")
elasticache_client = create_boto3_client("elasticache")
codedeploy_client = create_boto3_client("codedeploy")
codepipeline_client = create_boto3_client("codepipeline")
cloudtrail_client = create_boto3_client("cloudtrail")
athena_client = create_boto3_client("athena")
glue_client = create_boto3_client("glue")
transcribe_client = create_boto3_client("transcribe")
polly_client = create_boto3_client("polly")
rekognition_client = create_boto3_client("rekognition")
comprehend_client = create_boto3_client("comprehend")

# Bedrock client (錯誤處理)
try:
    bedrock_client = create_boto3_client("bedrock")
except Exception as e:
    bedrock_client = None
    print(f"Failed to initialize Bedrock client: {e}")

