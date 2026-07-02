#!/bin/bash

# ---------------------------------------
# Deploy Flask Weather Application
# ---------------------------------------

# 1. Update Ubuntu packages
sudo apt update -y
sudo apt upgrade -y

# 2. Install required software
sudo apt install python3 python3-pip python3.12-venv nginx git -y

# 3. Create a Python virtual environment
python3 -m venv venv

# 4. Activate the virtual environment
source venv/bin/activate

# 5. Install Python packages
pip install flask requests gunicorn

# 6. Stop any existing Gunicorn processes
pkill gunicorn

# 7. Start the Flask app with Gunicorn on port 5000
gunicorn --bind 127.0.0.1:5000 app:app --daemon

# 8. Configure Nginx as a reverse proxy to Gunicorn
sudo sed -i 's|try_files \$uri \$uri/ =404;|proxy_pass http://127.0.0.1:5000;\n        proxy_set_header Host \$host;\n        proxy_set_header X-Real-IP \$remote_addr;|' /etc/nginx/sites-available/default

# 9. Test Nginx configuration
sudo nginx -t

# 10. Restart Nginx
sudo systemctl restart nginx

echo "Deployment complete!"