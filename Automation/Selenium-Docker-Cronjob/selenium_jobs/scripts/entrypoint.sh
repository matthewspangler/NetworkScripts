#!/bin/bash

printenv | grep -v "foreman_email_1" >>/etc/environment
printenv | grep -v "foreman_password_1" >>/etc/environment

exec $@
