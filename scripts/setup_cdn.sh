#!/bin/bash
# Setup S3 bucket and CloudFront distribution for research assets
# Usage: ./scripts/setup_cdn.sh

set -e

BUCKET_NAME="behavioral-profiling-public"
REGION="us-west-2"

echo "=== Setting up CDN for behavioral-profiling ==="
echo ""

# Step 1: Create S3 bucket
echo "Step 1: Creating S3 bucket..."
aws s3api create-bucket \
    --bucket "$BUCKET_NAME" \
    --region "$REGION" \
    --create-bucket-configuration LocationConstraint="$REGION"

echo "Bucket created: $BUCKET_NAME"

# Step 2: Disable block public access (required for public bucket)
echo ""
echo "Step 2: Configuring public access..."
aws s3api put-public-access-block \
    --bucket "$BUCKET_NAME" \
    --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Step 3: Add bucket policy for public read
echo ""
echo "Step 3: Adding public read policy..."
cat > /tmp/bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket "$BUCKET_NAME" \
    --policy file:///tmp/bucket-policy.json

# Step 4: Enable CORS for browser access
echo ""
echo "Step 4: Enabling CORS..."
cat > /tmp/cors-config.json << EOF
{
    "CORSRules": [
        {
            "AllowedHeaders": ["*"],
            "AllowedMethods": ["GET", "HEAD"],
            "AllowedOrigins": ["*"],
            "ExposeHeaders": []
        }
    ]
}
EOF

aws s3api put-bucket-cors \
    --bucket "$BUCKET_NAME" \
    --cors-configuration file:///tmp/cors-config.json

# Step 5: Create CloudFront distribution
echo ""
echo "Step 5: Creating CloudFront distribution..."
cat > /tmp/cloudfront-config.json << EOF
{
    "CallerReference": "behavioral-profiling-$(date +%s)",
    "Comment": "CDN for behavioral-profiling research assets",
    "DefaultCacheBehavior": {
        "TargetOriginId": "${BUCKET_NAME}-origin",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"],
            "CachedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"]
            }
        },
        "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
        "Compress": true
    },
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "${BUCKET_NAME}-origin",
                "DomainName": "${BUCKET_NAME}.s3.${REGION}.amazonaws.com",
                "S3OriginConfig": {
                    "OriginAccessIdentity": ""
                }
            }
        ]
    },
    "Enabled": true,
    "PriceClass": "PriceClass_100"
}
EOF

DISTRIBUTION_OUTPUT=$(aws cloudfront create-distribution \
    --distribution-config file:///tmp/cloudfront-config.json)

DISTRIBUTION_ID=$(echo "$DISTRIBUTION_OUTPUT" | python3 -c "import sys, json; print(json.load(sys.stdin)['Distribution']['Id'])")
DISTRIBUTION_DOMAIN=$(echo "$DISTRIBUTION_OUTPUT" | python3 -c "import sys, json; print(json.load(sys.stdin)['Distribution']['DomainName'])")

echo ""
echo "=== Setup Complete ==="
echo ""
echo "S3 Bucket: $BUCKET_NAME"
echo "CloudFront Distribution ID: $DISTRIBUTION_ID"
echo "CloudFront Domain: https://$DISTRIBUTION_DOMAIN"
echo ""
echo "Save these values! Add to .env:"
echo ""
echo "CDN_BUCKET=$BUCKET_NAME"
echo "CDN_DISTRIBUTION_ID=$DISTRIBUTION_ID"
echo "CDN_DOMAIN=$DISTRIBUTION_DOMAIN"
echo ""
echo "Note: CloudFront may take 5-10 minutes to deploy fully."
echo ""
echo "Next step: Run 'python3 scripts/sync_research_assets.py' to upload assets."

# Cleanup
rm -f /tmp/bucket-policy.json /tmp/cors-config.json /tmp/cloudfront-config.json
