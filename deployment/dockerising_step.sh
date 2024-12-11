
cd pipeline

bash etl_docker_push.sh

bash upload_remove_subscribers_to_ecr.sh

cd ../streamlit_dashboard

bash streamlit_dashboard_upload.sh

echo "Files dockerised and uploaded to respective ECRs"


