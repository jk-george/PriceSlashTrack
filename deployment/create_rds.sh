cd terraform/terraform-rds
terraform init
terraform apply

cd ../..

PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -p $DB_PORT -f schema.sql

echo "Database has been setup"
