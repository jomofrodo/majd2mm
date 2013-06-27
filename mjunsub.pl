#!/usr/local/bin/perl 

### jomo 2/2005
### 8/2008
### helper for majordomo (?)
### Look for the original from address in a piece of forwarded e-mail -- unsub that address

### To use, set up procmailrc script in majordomo home directory with following entries:
### Forward remove request email to majordomo with Subject line of "unsub"
### mjunsub.pl will send an email to $majordomo with a Subject line of "Unsub Request for $email_address"

##### Unsubscribe requests
##:0fw
##* ^Subject:.*(unsubscribe|remove|REMOVE|Unsub Request)
##| /usr/local/majordomo/wrapper majordomo
##
##:0fw
##* ^Subject: unsub
##| /usr/local/majordomo/Tools/mjunsub.pl


## Config
my $local_adm	= 'mailadmin@netazoic.com';
my $logerr	= "/var/log/majordomo.log";
my $logfile	= "/var/log/majordomo.log";
my $list	= 'ccb';
my $majordomo	= 'majordomo@linus.netazoic.com';  
my $subject 	= "Unsub Request for ";
my $cmd		= "unsubscribe * ";
## my $majordomo = 'majordomo@netazoic.com';
##


while(@ARGV){
	$arg = shift(@ARGV);
	if( $arg eq '-l'){ $list = shift(@ARGV);}
	if( $arg eq '-r'){ $flgRcpt = 1;}
	if( $arg eq '-F'){ $flgLocalDom = 1;}  ## Accept fake local domain
}
my $flgFWTxt 	= "-----Original Message-----";
my $flgFW 	= 0;
my $flgFrom 	= 0;
my $txtRcvd 	= "Received:.*$local_dom";
my $flgAdm	= 1;
my $flgRcpt	= 0;
my $email	= '';
my $debug	= 0;

while (<STDIN>){
	if(0){print($_);}
	$email .= $_;

	## Check for end command
	if(/^end$/){ 
		## How do we do a last?
		while(<STDIN>){
			if(0){print($_);}
		}
		next;
	}
	## Check for forwarded email or requesting email address
	if (/^\s*?From:.*[\s:\<]\s*([\w\.]+@[\w\.]+)/){
		$unsub_email =$1;
		next;
	}
}

chomp($unsub_email);
## ltrim
$unsub_email =~ s/^\s+//;

if(! $unsub_email){
	$msg = "Unsub request does not look like a forwarded email.\n";
	$msg .= "Cannot process request from $from1\n";
	log_it($logfile,$msg);
	exit(1);
}
	
## Process the request
	$now = localtime;
	$cmd .= $unsub_email . "\n";
	$msg = $cmd;
	$msg .= "end \n";
	$msg .= ("$now \n");
	$msg .= ("Unsub request:\n");
	$msg .= ("From\: $from1\n");
	$msg .= ("For: $unsub_email\n\n\n");	

	#if($ret){
	#	$msg .= ("Unsubscribed $unsub_email from $list\n");
	#	$msg .= ("$ret\n");
	#}
	#else{
	#	$msg .= ("Request not processed.\n");
	#	if($debug){
	#		open ERR, ">> $logerr";
	#		select ERR;
	#		print "--------------------------------------------\n";
	#		print "$msg";
	#		print "--------------------------------------------\n";
	#		print "$email";
	#		close ERR;
	#		select STDOUT;
	#	}
	#}
	if($debug){ print($msg);}
	$subject .= $unsub_email;
	send_email($majordomo,$from1,$subject,$msg);
	#send_email($majordomo,$local_adm,$subject,$msg);
	log_it($logfile, $subject . "\n");
	#log_it($logfile,$msg);
	exit(0);
	
##########
# Log it #
##########
sub log_it{
	my($logfile, $msg) = @_;
	if($logfile){
		unless( open LOG, ">>$logfile") {
			die "Cannot open logfile: $!";
		}
		my $ts = Time_Stamp();
		select LOG;
		print "$ts: ";
		print "$msg";
		select STDOUT;
		close LOG;
	}
	return(0);
}
sub Time_Stamp {
        use vars qw($year $month $day  $hour $min $sec $len $stamp);
        # use standard function for date/time
        ($sec, $min, $hour, $day, $month, $year) = localtime();
        $year = 2000 + $year - 100;
        $month = $month +1;
        $len = length($year);
        if ($len < 2) {$year = "0$year"}
        $len = length($month);
        if ($len < 2) {$month = "0$month"}
        $len = length($day);
        if ($len < 2) {$day = "0$day"}

        $len = length($sec);
        if ($len < 2) {$sec = "0$sec"}
        $len = length($min);
        if ($len < 2) {$min = "0$min"}
        $len = length($hour);
        if ($len < 2) {$hour = "0$hour"}
        $stamp = "$year$month$day\-$hour" . "$min" . "$sec";
        return($stamp);
}

	
#########
# Email #
#########
sub send_email {
	my ($to_address, $from_address, $subject, $msg, $log_file, $bcc_address) = @_;
	my $MAIL_PROGRAM = '/usr/lib/sendmail -oi -t -odq';
	my (@a);
	if ($log_file) {
		open (LOG, "$log_file")  || return(0);
		@a = <LOG>;
		close (LOG);
	}

    open (MAIL, "|$MAIL_PROGRAM")
		or die "Can't fork for sendmail: $!\n";

	print MAIL "To: $to_address\n";
	if (defined($bcc_address)) {print MAIL "Bcc: $bcc_address\n";}
	print MAIL "From: $from_address\n";
	print MAIL "Subject: $subject\n\n";
	if ($msg) {print MAIL "$msg";}	
	if ($log_file) { print MAIL "@a";}
  	close (MAIL);
#warn "Sent email: To:  $to_address \nSubject: $subject" ;
	return (0);
}
	
