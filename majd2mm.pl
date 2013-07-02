#!/usr/bin/perl -w 

# Convert majordomo email commands to mailman email commands
# Jomo, 6/4/2013

my $email_body="";
my $cmd;
my $domainName = "linus.netazoic.com";
my $line;
my $from;

my $cmdSub = "http://[domain.name]/mailman/admin/[listname]/members/add?subscribees=[user_email_address]&adminpw=[admin_password]&send_welcome_msg_to_this_batch=0&send_notifications_to_list_owner=0";
my $cmdUnsub = "http://[domain.name]/mailman/options/[listname]/[user_email_address]?unsub=1&unsubconfirm=1&password=[admin_password]";

my $cmdMM;
my $logMsg;
my $flgUnsub = 0;


#************* SET THESE VALUES **************
my $MM_BIN="/usr/lib/mailman/bin";
my $MEMBERS_FILE="./members.txt";
my $LIST="ccb_genrl";
my $LOG_FILE="/var/log/majd2mm.log";
#********************************************

if(! -d $MM_BIN){ exit("The mailman bin directory not located. Please edit settings.");}


sub processCmd($){
	my($cmd1) = @_;
	my $ret;

	chomp($cmd1);


	if($cmd1 =~ /^approve.*/){
		$cmd1 =~ /approve\s+([\w|\.]+)\s+([\w]+)\s+([\w|_|\.|\*]+)\s+([\w|_|@|\.]+)/;
		$passwd = $1;
		$cmdVerb = $2;
		$list = $3;
		$email = $4;
	}
	elsif($cmd1 =~ /^unsubscribe\s+([\w|_|\*]+)\s+(.*)/){
		#$cmd1 =~ /unsubscribe\s+([\w|_|\*]+)\s+([\w|@|_|\.|\*]+)/;
		$cmdVerb = "unsubscribe";
		$list = $1;
		$email = $2;
	}
	else{
		$cmdVerb = "ERROR";
		$logMsg = "problem processing: $cmd1";
		return;
	}



	# Basic authentication is killing the wget idea
	#if($cmdVerb eq "subscribe"){ 
	#	$mmEmail = "join-$list";
	#	$cmdMM = $cmdSub;
	#}
	#if($cmdVerb=~/unsub/i){ 
	#	$mmEmail = 
	#	$cmdMM = $cmdUnsub;
	#}
	#$cmdMM =~s/\[domain.name\]/$domainName/;
	#$cmdMM =~s/\[listname\]/$list/;
	#$cmdMM =~s/\[user_email_address\]/$email/;
	#$cmdMM =~s/\[admin_password\]/$passwd/;
	#system("wget $cmdMM");



	# Email options aren't all that great
	#$mmEmail = $cmdVerb . "_" . $list;
	#$msg = "subscribe address=$email";	
	#$from = $majordomoEmail;
	#send_email($mmEmail,$from,$subject,$msg);

	# Just run commands directly

	&writeMembers($email);
	if($cmdVerb eq "subscribe"){
	
		# just run the add_members command
		$cmd = "$MM_BIN/add_members -r $MEMBERS_FILE $LIST";
		$cmd .=" -w y -a n";
		$cmd .= " $list";
		$ret = `$cmd`;
		if(! $?){$logMsg = $list . ": " . $ret}
		else{	$logMsg = "Error while trying to subscribe $email to $list\n";
			$logMsg .= "$ret\n";
			}
	}
	elsif($cmdVerb eq "unsubscribe"){

		$email=~s/\*//g;  # remove wildcards in the email address
		$cmd = "$MM_BIN/remove_members ";
		if($list eq "*"){ $cmd .= " --fromall";}
		else{ $cmd .= " $list ";}
		$cmd .= " $email";
		$ret = `$cmd`;
		if(! $?){
			if($ret){$logMsg = $ret;}
			#else{$logMsg = "Ran unsubscribe command with no results: $cmd";}
			else{$logMsg = "Unsubscribed $email from $list";}
		}
		else{	$logMsg = "Error while trying to unsubscribe $email from $list\n";
			$logMsg .= "$ret\n";
		}
	   
	}
	&writeLog($LOG_FILE, $logMsg);

}
	
	

while (<STDIN>){

	if(1){print($_);}
	$email_body .= $_;
	$line = $_;
	if(! $line){ next;}
	chomp($line);
	if(! $line){ next;}
	if ($line=~/^\s*From:.*[\s:\<]\s*([\w\.]+@[\w\.]+)/){
		$from = $1;next;
	}
	if($line=~/^\s+?approve.*/){
		$cmd = $line;
		processCmd($cmd);
		next;
	}
	if($line=~/^\s+?unsubscribe.*/){
		$cmd = $line;
		processCmd($cmd);
		next;
	}
	if($line=~/Subject:.*(unsub|remove)/i){
		$flgUnsub = 1;

		#Have to process this command outside the main loop as we can't be sure
		#the subject line will follow the From line

		#$cmd = "approve ccb.passwd unsubscribe * $from";
		#processCmd($cmd);
		next;
	}
	if(/^end$/){ 
		## How do we do a last?
		while(<STDIN>){
			if(0){print($_);}
		}
		next;
	}
	next;
	
}	

if($flgUnsub && $from){
# Special purpose -- process a user submitted remove or unsub command
		$cmd = "approve ccb.passwd unsubscribe * $from";
		processCmd($cmd);
		$flgUnsub = 0;
}



sub writeLog{
# write anything out to a log file
        ($logfile,$logtext) = @_;
	chomp($logtext);
	if($logtext!~/.*\n$/){
		$logtext .= "\n";
	}
        open (FH,">>$logfile");
        print FH $logtext;
        close FH;
        return;
}


sub writeMembers{
	my $memfile = $MEMBERS_FILE;
	my ($members) = @_;
	unlink($memfile);	# zero it out
	open(FH, ">>$memfile");
	print(FH $members);
	close FH;
	return;
}

=begin GHOSTCODE
=end GHOSTCODE
