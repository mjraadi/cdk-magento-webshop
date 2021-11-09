#!/bin/bash -xe

# Log EC2 Linux user data and then ship it to the console logs
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "Hello from user-data!"
# define variables
EFS_ID="${__EFS_ID__}"
EFS_ACCESS_POINT_ID="${__EFS_ACCESS_POINT_ID__}"

# install the required packages
sudo yum update -y
sudo yum -y install amazon-efs-utils

# mount EFS resource
sudo mkdir -p /efs
sudo mount -t efs -o tls,accesspoint=${!EFS_ACCESS_POINT_ID} ${!EFS_ID}:/ /efs
echo hello > /efs/hello.txt
ls -la /efs
