# Provisioning

You can use the files contained in this directory to provision
your machine in order to make the project working.

To start quickly edit the ``ansible_deploy_inventory`` and ``ansible_deploy_variables``
files following your taste and then

    $ cd provision/
    $ bin/ansible -i ansible_deploy_inventory -v ansible_deploy_variables



## Ansible

Use the 2.0+ version.

## Vagrant

Out of the box is available a Debian8 virtualbox configuration, you have
to do a simple

    $ vagrant up --provider virtualbox

If you want to login with the user

    $ ssh -i id_rsa_my_project my_project@127.0.0.1 -p 2222 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no

If you want to copy something inside you can do

    $ scp -i id_rsa_my_project -P 2222 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no foobar.py  my_project@127.0.0.1:app/



## Nginx

The web server listen only ``HTTPS`` (un-encrypted requests are redirect to encrypted ones).

It's configured to use self-signed certificate, the real one must be generated and certificate
and private key be in the correct places (look at ``/etc/nginx/site-available/ktln2``).

