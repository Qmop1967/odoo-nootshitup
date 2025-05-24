pwd
pwd
r
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
git clone https://github.com/odoo/odoo.git -b 18.0 odoo-18.0 && git clone https://github.com/odoo/enterprise.git -b 18.0 odoo-18.0/enterprise
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && ls -la
gh --version
apt update && apt install -y gh
gh auth login
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
apt install -y postgresql postgresql-contrib
systemctl start postgresql && systemctl enable postgresql
sudo -u postgres createuser -s $USER
cd /opt/odoo
mkdir -p /var/log/odoo && mkdir -p /opt/odoo/.local/share/Odoo
source odoo-venv/bin/activate && python odoo-community/odoo-bin --help | head -10
source odoo-venv/bin/activate && python odoo-community/odoo-bin -c odoo.conf --init=base --stop-after-init
sleep 5 && curl -I http://localhost:8069
ps aux | grep odoo-bin
tail -20 /var/log/odoo/odoo.log
sleep 10 && curl -I http://localhost:8069
tail -30 /var/log/odoo/odoo.log
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
source odoo-venv/bin/activate && python odoo-community/odoo-bin -c odoo.conf --dev=reload,qweb,werkzeug,xml
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && python odoo-community/odoo-bin -c odoo.conf
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && python odoo-community/odoo-bin -c odoo.conf
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && chmod +x get_zoho_tokens.py && python get_zoho_tokens.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && python /opt/odoo/odoo-community/odoo-bin -c /opt/odoo/odoo.conf -d odtshbrain --stop-after-init --log-level=warn
systemctl stop odoo && sleep 5 && systemctl status odoo
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
dpkg -l | grep odoo
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
sudo -u postgres psql -c "ALTER USER root WITH PASSWORD 'odoo123';"
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
ps aux | grep odoo
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
pip list | grep -i odoo
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
sudo -u postgres psql -c "ALTER USER root WITH PASSWORD 'odoo123';"
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
netstat -tlnp | grep :8069
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && ls -la
python3 -m venv odoo-venv
source odoo-venv/bin/activate && pip install --upgrade pip
ls -la
source ./odoo-venv/bin/activate && pip install --upgrade pip
ls -la odoo-venv/
ls -la odoo-venv/bin/
rm -rf odoo-venv && python3 -m venv odoo-venv --prompt odoo
ls -la odoo-venv/bin/
source odoo-venv/bin/activate && pip install --upgrade pip wheel
source odoo-venv/bin/activate && pip install -r odoo-community/requirements.txt
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
ls -la /etc/systemd/system/ | grep odoo
find /opt -name "*odoo*" 2>/dev/null
find /usr -name "*odoo*" 2>/dev/null
git --version
python3 --version && pip3 --version
mkdir -p /opt/odoo && cd /opt/odoo
cd /opt/odoo && pwd
cd /opt/odoo && git clone https://github.com/odoo/odoo.git --depth 1 --branch 18.0 --single-branch odoo-community
ssh -T git@github.com
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
systemctl status odoo
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
which odoo
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && pwd
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && python odoo-community/odoo-bin -c odoo_test.conf --init=base,account,sale,purchase,stock,website --stop-after-init --without-demo=False
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && ls -la
git clone https://github.com/odoo/enterprise.git --depth 1 --branch 18.0 --single-branch odoo-enterprise
ls -la
apt install -y python3-dev python3-pip python3-venv libxml2-dev libxslt1-dev libevent-dev libsasl2-dev libldap2-dev pkg-config libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev libfribidi-dev libxcb1-dev libpq-dev
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
apt update && apt upgrade -y
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
pkill -f odoo-bin
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
sudo apt update && sudo apt install -y git python3-pip python3-dev python3-venv build-essential libxslt-dev libzip-dev libldap2-dev libsasl2-dev python3-setuptools node-less libjpeg-dev libpq-dev libxml2-dev libffi-dev libssl-dev libmysqlclient-dev libjpeg8-dev liblcms2-dev libblas-dev libatlas-base-dev libpng-dev libtiff-dev libopenjp2-7-dev libwebp-dev libharfbuzz-dev libfribidi-dev libxcb1-dev npm && sudo npm install -g rtlcss
sudo apt install -y postgresql && sudo -u postgres createuser -s $USER
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && ls -la odoo_test.conf
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
chmod +x /opt/odoo/migration/get_zoho_tokens.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python get_zoho_tokens.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python get_zoho_tokens_simple.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python test_zoho_connection.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
ps aux | grep odoo
cd /opt/odoo
cd /opt/odoo && mkdir -p /opt/odoo/.local/share/Odoo_test && mkdir -p /var/log/odoo
cd /opt/odoo && source odoo-venv/bin/activate && python odoo-community/odoo-bin -c odoo_test.conf --init=base,account,sale,purchase,stock,website --stop-after-init --without-demo=False
sudo -u postgres psql -l | grep odtshbrain
cd /opt/odoo/migration && python setup_zoho_auth.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python debug_tokens.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && cat config/zoho_config.json | grep refresh_token
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python test_zoho_connection.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && curl -s http://localhost:8070/web/database/manager | grep -o "odtshbrain_test" || echo "Test DB check failed"
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python -c "import json; config=json.load(open('config/zoho_config.json')); print('Books:', config['zoho_books']['refresh_token']); print('Inventory:', config['zoho_inventory']['refresh_token'])"
cd /opt/odoo/migration && rm config/zoho_config.json
cd /opt/odoo/migration && python update_config.py
cd /opt/odoo/migration && python3 update_config.py
cd /opt/odoo/migration && python3 debug_tokens.py
cd /opt/odoo/migration && python3 -c "import json; config=json.load(open('config/zoho_config.json')); print('Books URL:', config['zoho_books']['base_url']); print('Inventory URL:', config['zoho_inventory']['base_url'])"
cd /opt/odoo/migration && python3 update_config.py
cd /opt/odoo/migration && python3 debug_tokens.py
cd /opt/odoo/migration && python3 test_zoho_connection.py
cd /opt/odoo/migration && ls -la
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && sudo systemctl status odoo-test || echo "Test service not found"
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
sleep 5 && ps aux | grep "odoo_test.conf" | grep -v grep
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
netstat -tlnp | grep 8070
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && cd migration && python zoho_odoo_migrator.py test
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && cd migration && python test_odoo_connection.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && ls -la logs/
cd /opt/odoo/migration && cat logs/migration.log
ps aux | grep "zoho_odoo_migrator" | grep -v grep
cd /opt/odoo/migration && tail -20 logs/migration.log
cd /opt/odoo && source odoo-venv/bin/activate && pip list | grep odoorpc
cd /opt/odoo && source odoo-venv/bin/activate && pip install odoorpc
pkill -f "zoho_odoo_migrator.py"
cd /opt/odoo/migration && python test_odoo_connection.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
chmod +x /opt/odoo/start_test_odoo.sh && /opt/odoo/start_test_odoo.sh
ss -tlnp | grep 8070 || echo "Port 8070 not found with ss, trying lsof..."
curl -s http://localhost:8070/web/database/manager | grep -o "odtshbrain_test" || echo "Test DB not found"
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
sudo -u postgres psql -c "SELECT datname FROM pg_database WHERE datname='odtshbrain_test';"
curl -s "http://localhost:8070/web/database/manager" | grep -i "create database" || echo "Database manager not accessible"
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
sleep 30 && ps aux | grep "odoo_test.conf" | grep -v grep
cd /opt/odoo && source odoo-venv/bin/activate && nohup python /opt/odoo/odoo-community/odoo-bin -c /opt/odoo/odoo_test.conf > /var/log/odoo/odoo_test.log 2>&1 &
sleep 10 && ss -tlnp | grep 8070
cd /opt/odoo/migration && python3 update_passwords.py
cd /opt/odoo/migration && python3 test_odoo_connection.py
cd /opt/odoo && source odoo-venv/bin/activate && cd migration && python test_odoo_connection.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && cd migration && python zoho_odoo_migrator.py test
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && cat logs/migration.log
cd /opt/odoo && source odoo-venv/bin/activate && cd migration && python simple_test_migration.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && sleep 10 && cat logs/migration.log | tail -20
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
sleep 30 && echo "Checking test results..."
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && ps aux | grep "zoho_odoo_migrator" | grep -v grep
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
fuser -k 8070/tcp || echo "Port 8070 cleared"
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && cd migration && python extract_zoho_data.py
cd /opt/odoo/migration && ls -la data/extracted/
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
ps aux | grep "simple_test_migration" | grep -v grep
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
curl -s http://localhost:8070/web/login | grep -i "odoo" || echo "Odoo web interface not accessible"
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
pkill -f "odoo_test.conf" && sleep 5 && ps aux | grep "8070" | grep -v grep
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
chmod +x /opt/odoo/fix_test_odoo.sh && /opt/odoo/fix_test_odoo.sh
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
ss -tlnp | grep 8070
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
sleep 60 && echo "Checking Odoo test instance status..."
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
ss -tlnp | grep 8070
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
ps aux | grep "odoo_test.conf" | grep -v grep
tail -10 /var/log/odoo/odoo_test_startup.log
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
pkill -9 -f "odoo-bin" && sleep 5 && sudo fuser -k 8070/tcp
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && timeout 30 python reset_admin_temp.py
cd /opt/odoo && source odoo-venv/bin/activate
python /opt/odoo/migration/run_full_migration.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
netstat -tlnp | grep 8070 || echo "Port 8070 not listening"
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
sleep 30 && ps aux | grep "odoo_test.conf" | grep -v grep
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && tail -f logs/migration.log
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && nohup python /opt/odoo/odoo-community/odoo-bin -c /opt/odoo/odoo_test.conf --logfile=/var/log/odoo/odoo_test.log > /dev/null 2>&1 &
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && python /opt/odoo/odoo-community/odoo-bin -c /opt/odoo/odoo_test.conf --test-enable --stop-after-init
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && cd migration && python test_passwords.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && python /opt/odoo/odoo-community/odoo-bin -c /opt/odoo/odoo_test.conf -d odtshbrain_test -i base --stop-after-init --without-demo=all
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && python /opt/odoo/odoo-community/odoo-bin -c /opt/odoo/odoo_test.conf -d odtshbrain_test --stop-after-init --log-level=warn
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && cd migration && timeout 60 python fix_admin_permissions.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && tail -f logs/migration_$(date +%Y%m%d).log
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python fix_admin_permissions.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
sleep 15 && ss -tlnp | grep 8070
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 migrate_contacts_enhanced.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 migrate_contacts_enhanced.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 quick_status.py
cd /opt/odoo/migration && python3 check_product_status.py
cd /opt/odoo/migration && chmod +x continuous_sync_server.py sync_monitor.py start_sync_server.py
cd /opt/odoo/migration && python3 -c "from continuous_sync_server import ContinuousSyncServer; print('🔄 Testing sync server...'); s = ContinuousSyncServer(); print('✅ Sync server initialized successfully'); print('📊 Config loaded: Zoho + Odoo connections ready'); print('🎯 Ready to start continuous synchronization')"
cd /opt/odoo/migration && python3 quick_status.py
cd /opt/odoo/migration && ls -la *.py *.service *.md | grep -E "(continuous_sync|sync_monitor|start_sync|SYNC_SERVER|zoho-odoo-sync)"
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
find /opt -name "*odoo*" -type d 2>/dev/null | head -10
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 sync_pricelists_only.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 list_active_pricelists.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
tail -20 /opt/odoo/migration/logs/full_migration.log
cd /opt/odoo && source odoo-venv/bin/activate && python3 -c "import xmlrpc.client; url='http://localhost:8069'; db='odtshbrain'; username='khaleel@tsh.sale'; password='Zcbm.97531tsh'; common=xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common'); uid=common.authenticate(db,username,password,{}); models=xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object'); field_info=models.execute_kw(db,uid,password,'product.template','fields_get',['type']); print('Product type field:'); print(field_info['type'])"
cd /opt/odoo/migration && python3 test_product_migration.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python test_zoho_connection.py
cd /opt/odoo/migration && python3 test_zoho_connection.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
systemctl status odoo
bash /opt/odoo/start_odoo_and_migrate.sh
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
ps aux | grep migrate_products_only | grep -v grep
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
ps aux | grep test_product_migration
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && ls -la *.log 2>/dev/null || echo "No log files in current directory"
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && python3 -c "import xmlrpc.client; url='http://localhost:8069'; db='odtshbrain'; username='khaleel@tsh.sale'; password='Zcbm.97531tsh'; common=xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common'); uid=common.authenticate(db,username,password,{}); models=xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object'); count=models.execute_kw(db,uid,password,'product.template','search_count',[[]]); print(f'Total products in Odoo: {count}')"
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
tail -30 /opt/odoo/migration/logs/full_migration.log
ps aux | grep "run_full_migration\|python.*migration" | grep -v grep
sleep 10 && ps aux | grep migrate_products_only
tail -f /var/log/syslog | grep -i "migrate\|product" | head -20
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
curl -s http://localhost:8069/web/database/manager | grep -q "odtshbrain" && echo "✅ Odoo is running" || echo "❌ Odoo not accessible"
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
pwd && ls -la
cd /opt/odoo/migration && ls -la
cd /opt/odoo/migration && chmod +x fix_duplicate_contacts.py migrate_contacts_no_duplicates.py
cd /opt/odoo/migration && python3 fix_duplicate_contacts.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
log_file=$(find /opt/odoo/migration/logs -name "contact_migration_*.log" -print0 | xargs -0 ls -t | head -1) && if [ -n "$log_file" ]; then echo "Found log: $log_file"; tail -n 50 "$log_file"; else echo "No specific contact migration log file found yet. Checking general logs."; tail -n 50 /opt/odoo/migration/logs/migration.log 2>/dev/null || echo "No migration.log found."; fi
ps aux | grep migrate_contacts_enhanced.py | grep -v grep
systemctl status odoo
sudo systemctl start odoo
sleep 15 && systemctl status odoo
sudo journalctl -u odoo -n 50 --no-pager
sudo lsof -t -i:8069
sudo kill 71382 && echo 'Killed 71382' || echo 'PID 71382 not found'
sudo kill 61088 && echo 'Attempted to kill PID 61088' || echo 'PID 61088 not found or already killed'
sudo lsof -t -i:8069
sudo systemctl start odoo && sleep 15 && systemctl status odoo
sleep 60 && echo "--- Checking Odoo Status ---" && systemctl is-active odoo && echo "--- Checking Contact Migration Process ---" && ps aux | grep migrate_contacts_enhanced.py | grep -v grep || echo "Contact migration process not found."
cd /opt/odoo/migration && python3 migrate_contacts_enhanced.py
sleep 45 && echo "--- Checking Odoo Status ---" && systemctl is-active odoo && echo "--- Checking Contact Migration Process ---" && ps aux | grep migrate_contacts_enhanced.py | grep -v grep || echo "Contact migration process not found."
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && chmod +x quick_duplicate_check.py && python3 quick_duplicate_check.py
cd /opt/odoo/migration && chmod +x resolve_duplicates_interactive.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && python3 -c "import xmlrpc.client; url='http://localhost:8069'; db='odtshbrain'; username='khaleel@tsh.sale'; password='Zcbm.97531tsh'; common=xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common'); uid=common.authenticate(db,username,password,{}); models=xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object'); count=models.execute_kw(db,uid,password,'res.partner','search_count',[[]]); print(f'Total contacts (res.partner records) in Odoo: {count}')"
sleep 120 && echo "--- Checking Odoo Status ---" && systemctl is-active odoo && echo "--- Checking Contact Migration Process ---" && ps aux | grep migrate_contacts_enhanced.py | grep -v grep || echo "Contact migration process not found."
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && ls -la *duplicate* *no_duplicates* *.md | grep -E "(duplicate|no_duplicates|\.md)"
cd /opt/odoo/migration && ls -la | grep -E "(duplicate|no_duplicates|\.md)"
cd /opt/odoo/migration && echo "1" | python3 resolve_duplicates_interactive.py | head -30
# 1. Navigate to migration directory
cd /opt/odoo/migration
# 2. See the scope of the problem
python3 quick_duplicate_check.py
# 3. Run the interactive resolver
python3 resolve_duplicates_interactive.py
# Choose option 1 for dry run first, then option 2 to remove with backup
# 4. Verify the cleanup worked
python3 quick_duplicate_check.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && chmod +x run_duplicate_fix.py && python3 run_duplicate_fix.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 resolve_duplicates_interactive.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 change_currency_to_iqd.py
cd /opt/odoo/migration && python3 change_currency_to_iqd_fixed.py
cd /opt/odoo/migration && python3 change_currency_direct.py
echo "💡 Ready to run complete migration once currency is changed to IQD"
sleep 10 && ps aux | grep enhanced_product_migrator | grep -v grep
sleep 30 && ps aux | grep enhanced_product_migrator | grep -v grep
sleep 60 && ps aux | grep enhanced_product_migrator | grep -v grep || echo "Migration completed"
find /opt/odoo/migration -name "*.log" -newer /opt/odoo/migration/enhanced_product_migrator.py 2>/dev/null | head -5
jobs
cd /opt/odoo && source odoo-venv/bin/activate && python3 -c "import xmlrpc.client; url='http://localhost:8069'; db='odtshbrain'; username='khaleel@tsh.sale'; password='Zcbm.97531tsh'; common=xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common'); uid=common.authenticate(db,username,password,{}); models=xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object'); count=models.execute_kw(db,uid,password,'product.template','search_count',[[]]); print(f'Total products in Odoo: {count}')"
ps aux | grep enhanced_product_migrator | grep -v grep
while ps aux | grep enhanced_product_migrator | grep -v grep > /dev/null; do echo "$(date): Migration still running..."; sleep 30; done && echo "Migration completed!"
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
sleep 30 && ps aux | grep migrate_contacts_enhanced.py | grep -v grep
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && echo "1" | python3 resolve_duplicates_interactive.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && echo "1" | python3 run_duplicate_fix.py
cd /opt/odoo/migration && python3 quick_duplicate_check.py
cd /opt/odoo/migration && ls -la *product*
cd /opt/odoo/migration && pip3 install schedule
cd /opt/odoo/migration && pip3 install schedule --break-system-packages && chmod +x zoho_product_sync.py product_sync_scheduler.py
cd /opt/odoo/migration && python3 product_sync_scheduler.py status
cd /opt/odoo/migration && echo "2" | python3 zoho_product_sync.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && ps aux | grep fix_duplicate_contacts
cd /opt/odoo/migration && python3 fix_duplicate_contacts.py | head -50
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
find . -name "*.py" -o -name "*.xml" -o -name "*.csv" -o -name "*migration*" -o -name "*product*" | head -20
find . -type d -name "*odoo*" -o -name "*migration*" -o -name "*product*" 2>/dev/null
find . -name "*.py" -mtime -7 -not -path "./.cursor-server/*" 2>/dev/null | head -10
ls -la
tail -20 .bash_history | grep -E "(migration|product|odoo|zoho)" -i
cd /opt/odoo/migration && ls -la
cd /opt/odoo/migration && python3 check_product_status.py
cd /opt/odoo/migration && chmod +x fix_product_migration_issues.py check_product_status.py test_fixes.py zoho_product_sync_enhanced.py
cd /opt/odoo/migration && python3 test_fixes.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 check_product_status.py
cd /opt/odoo/migration && python3 fix_usd_to_iqd_automated.py
cd /opt/odoo/migration && python3 run_image_fetch.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 run_duplicate_removal.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && chmod +x fix_usd_to_iqd_automated.py && python3 fix_usd_to_iqd_automated.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 zoho_product_sync_enhanced.py
cd /opt/odoo/migration && chmod +x simple_image_fetch.py && python3 simple_image_fetch.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 fix_product_migration_issues.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 -c "import sync_active_pricelists_only; print('Script imported successfully')"
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && tail -n 50 logs/active_pricelist_sync.log
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && ls -la logs/
cd /opt/odoo/migration && python3 sync_active_pricelists_only.py 2>&1 | head -n 50
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && chmod +x sync_active_pricelists_only.py && python3 sync_active_pricelists_only.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 sync_active_pricelists_only.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
chmod +x /opt/odoo/migration/sync_pricelists_only.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && timeout 30 python3 sync_active_pricelists_only.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 quick_status.py
cd /opt/odoo/migration && python3 check_product_status.py
cd /opt/odoo/migration && chmod +x run_image_fetch_batches.py && python3 run_image_fetch_batches.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && ls -la logs/ | grep active
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 run_full_migration.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
tail -f /opt/odoo/migration/logs/migration_$(date +%Y%m%d).log
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 migrate_contacts_enhanced.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 migrate_products_only.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 enhanced_product_migrator.py
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
tail -f /opt/odoo/migration/logs/full_migration.log
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo && source odoo-venv/bin/activate && python3 -c "import xmlrpc.client; url='http://localhost:8069'; db='odtshbrain'; username='khaleel@tsh.sale'; password='Zcbm.97531tsh'; common=xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common'); uid=common.authenticate(db,username,password,{}); models=xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object'); count=models.execute_kw(db,uid,password,'res.partner','search_count',[[]]); print(f'Total contacts (res.partner records) in Odoo: {count}')"
sleep 180 && echo "--- Checking Odoo Status ---" && systemctl is-active odoo && echo "--- Checking Contact Migration Process ---" && ps aux | grep migrate_contacts_enhanced.py | grep -v grep || echo "Contact migration process likely completed or stopped."
. "\root\.cursor-server\cli\servers\Stable-96e5b01ca25f8fbd4c4c10bc69b15f6228c80770\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && python3 continuous_sync_server_enhanced.py
. "\root\.cursor-server\cli\servers\Stable-f3f2ad556456ff2df80332923bb1e2a818110d10\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
tail -50 /opt/odoo/migration/logs/sync_server_enhanced.log
. "\root\.cursor-server\cli\servers\Stable-f3f2ad556456ff2df80332923bb1e2a818110d10\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && chmod +x zoho_odoo_sync_service.py sync_service_manager.py add_zoho_field.py
cd /opt/odoo/migration && python3 add_zoho_field.py
cd /opt/odoo/migration && python3 sync_service_manager.py install
. "\root\.cursor-server\cli\servers\Stable-f3f2ad556456ff2df80332923bb1e2a818110d10\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd /opt/odoo/migration && echo "ARCHIVE" | python3 clean_import_safe.py
python3 sync_service_manager_fixed.py sync-once
. "\root\.cursor-server\cli\servers\Stable-f3f2ad556456ff2df80332923bb1e2a818110d10\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
systemctl status zoho-odoo-sync zoho-odoo-sync-images
