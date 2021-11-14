#!/bin/bash -xe

# Log EC2 Linux user data and then ship it to the console logs
exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

# define variables
AWS_ACCOUNT_ID="${__AWS_ACCOUNT_ID__}"
AWS_REGION="${__AWS_REGION__}"
MYSQL_INSTANCE_ADDRESS="${__MYSQL_INSTANCE_ADDRESS__}"
MYSQL_SECRET_NAME="${__MYSQL_SECRET_NAME__}"
CF_DISTRIBUTION_DOMAIN_NAME="${__CF_DISTRIBUTION_DOMAIN_NAME__}"

echo "Hello from user-data!"
# install the required packages
yum update -y
yum -y install mysql git httpd jq amazon-linux-extras amazon-efs-utils
amazon-linux-extras enable php7.3
yum clean metadata
yum install -y php php-{pear,dev,ctype,cgi,dom,common,curl,mbstring,gd,pdo,mysqlnd,simplexml,iconv,gettext,bcmath,json,xml,fpm,intl,zip,imap,soap,xsl,opcache,xmlrpc,phpdbg}
php -v && echo "PHP installed successfully"

# retriveing mysql credentials from secrets manager
MYSQL_USER=$(aws secretsmanager get-secret-value \
  --region ${!AWS_REGION} --secret-id ${!MYSQL_SECRET_NAME} \
--query SecretString --output text | jq -r .username)

MYSQL_PWD=$(aws secretsmanager get-secret-value \
  --region ${!AWS_REGION} --secret-id ${!MYSQL_SECRET_NAME} \
--query SecretString --output text | jq -r .password)

# testing mysql connection
# TODO: the password will be visible on user data logs. find a way
# to prevent this
mysql -h ${!MYSQL_INSTANCE_ADDRESS} -u ${!MYSQL_USER} \
-p${!MYSQL_PWD} -e"quit" &&
echo "connecting to MySQL server was successful"

# configuring php memory limit
sed -i 's/memory_limit\s*=.*/memory_limit=1024M/g' /etc/php.ini
systemctl enable httpd
systemctl start httpd

# adding ec2-user to the webservers group and setting correct
# file and directory permissions on /var/www
usermod -a -G apache ec2-user
cd /var/www/
chown -R ec2-user:apache /var/www
chmod 2775 /var/www
find /var/www -type d -exec chmod 2775 {} +
find /var/www -type f -exec chmod 0664 {} +

# installing php composer
export COMPOSER_HOME=/root
sudo curl -sS https://getcomposer.org/installer | sudo php
mv composer.phar /usr/bin/composer
chmod +x /usr/bin/composer

# download magento 2.3.7 version, extract its content to
# /var/www/html directory
wget -c https://github.com/magento/magento2/archive/refs/tags/2.3.7.tar.gz -O - | tar -xz --directory /var/www/html/ --strip 1
cd /var/www/html

# installing magento 2 dependencies
COMPOSER_ALLOW_SUPERUSER=1 /usr/bin/composer install

# setting proper file and directory permissions for magento files
find var generated vendor pub/static pub/media app/etc -type f -exec chmod g+w {} +

find var generated vendor pub/static pub/media app/etc -type d -exec chmod g+ws {} +

chown -R :apache .

chmod u+x bin/magento

# install magento
bin/magento setup:install \
--base-url=http://${!CF_DISTRIBUTION_DOMAIN_NAME}/ \
--db-host=${!MYSQL_INSTANCE_ADDRESS} \
--db-name=webshop \
--db-user=${!MYSQL_USER} \
--db-password=${!MYSQL_PWD} \
--admin-firstname=admin \
--admin-lastname=admin \
--admin-email=admin@admin.com \
--admin-user=admin \
--admin-password=${!MYSQL_PWD}@ \
--language=en_US \
--currency=USD \
--timezone=America/Chicago \
--use-rewrites=1

# configure Magento URLs
php bin/magento config:set web/unsecure/base_url http://${!CF_DISTRIBUTION_DOMAIN_NAME}/
php bin/magento config:set web/unsecure/base_link_url http://${!CF_DISTRIBUTION_DOMAIN_NAME}/
php bin/magento config:set web/secure/enable_upgrade_insecure 1
php bin/magento config:set web/secure/base_url https://${!CF_DISTRIBUTION_DOMAIN_NAME}/
php bin/magento config:set web/secure/base_link_url https://${!CF_DISTRIBUTION_DOMAIN_NAME}/
php bin/magento config:set web/secure/use_in_frontend 1
php bin/magento config:set web/secure/use_in_adminhtml 1
php bin/magento config:set web/url/redirect_to_base 0

# clean magento cache and recompile static assets
php bin/magento cache:clean
php bin/magento setup:di:compile
php bin/magento setup:static-content:deploy -f

# a hacky workaround to fix 404 error issue for static assets after
# installation
static_version=$(cat pub/static/deployed_version.txt)
mkdir -p pub/static/version${!static_version}
cp -R pub/static/frontend pub/static/version${!static_version}/
