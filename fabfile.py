from fabric.context_managers import cd, settings
from fabric.operations import sudo, run
from fabric.state import env

env.hosts = ['root@104.236.113.169']

def deploy_dev():
    code_dir = '/var/www/mlmportal/'
    with cd(code_dir):

        # with settings(warn_only=True):
        #     run('mv MLM/settings.py MLM/settingsold.py')
        run("git pull")
        ## run('ls ../')
        ## run('ls ../settings')
        # sudo('cp /root/settings.py MLM/settings.py')
        # sudo('chown django:django MLM/settings.py')
        run('source venv/bin/activate')
        run('pip install -r requirements.txt')
        # run('python manage.py collectstatic --noinput')
        # run('python manage.py migrate')
        # sudo('service gunicorn stop')
        # sudo('service gunicorn start')
