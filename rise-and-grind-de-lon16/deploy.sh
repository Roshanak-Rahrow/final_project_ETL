#!/usr/bin/sh
#STOP ON ERROR
set -eu
###
### Script to deploy S3 bucket + lambda in cloudformation stack
###

#### CONFIGURATION SECTION ####
aws_profile="de-course"
team_name="rise-and-grind" 
deployment_bucket="${team_name}-deployment-bucket"

# EC2 config
ec2_ingress_ip="0.0.0.0" # e.g. 12.34.56.78 (of your laptop where you are running this)

deployment_bucket="${team_name}-deployment-bucket"
ec2_userdata=$(base64 -i userdata)

#### CONFIGURATION SECTION ####
echo ""
echo "Doing deployment bucket..."
echo ""

aws cloudformation deploy \
    --stack-name "${team_name}-etl-lambda" \
    --template-file deployment-bucket-stack.yml \
    --region eu-west-1 \
    --capabilities CAPABILITY_IAM \
    --profile ${aws_profile} \
    --parameter-overrides TeamName="${team_name}";
        

#INTSTALL DEPENDENCIES
if [ -z "${SKIP_PIP_INSTALL:-}" ]; then
    echo ""
    echo "Doing pip install..."
    python -m pip install --platform manylinux2014_x86_64 \
        --target=./src --implementation cp --python-version 3.12 \
        --only-binary=:all: --upgrade -r requirements-lambda.txt;

else
    echo ""
    echo "Skipping pip install"
fi

# Create an updated ETL packaged template "etl-stack-packaged.yml" from the default "etl-stack.yml"
# ...and upload local resources to S3 (e.g zips files of your lambdas)
# A unique S3 filename is automatically generated each time
echo ""
echo "Doing packaging..."
echo ""
aws cloudformation package --template-file etl-stack.yml \
    --s3-bucket ${deployment_bucket} \
    --output-template-file etl-stack-packaged.yml \
    --profile ${aws_profile};

# Deploy the main ETL stack using the packaged template "etl-stack-packaged.yml"
echo ""
echo "Doing etl stack deployment..."
echo ""
aws cloudformation deploy \
    --stack-name "${team_name}-etl-pipeline" \
    --template-file etl-stack-packaged.yml \
    --region eu-west-1 \
    --capabilities CAPABILITY_IAM \
    --profile ${aws_profile} \
    --parameter-overrides \
        TeamName="${team_name}" \
        EC2InstanceIngressIp="${ec2_ingress_ip}" \
        EC2UserData="${ec2_userdata}";

echo ""
echo "...all done!"
echo ""
