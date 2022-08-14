#!/bin/sh
cat /home/fbr.mailadmin/bin/test/test.subscribe.txt | sendmail fbr.test
tail /home/fbr.mailadmin/procmail/2022Aug.log
