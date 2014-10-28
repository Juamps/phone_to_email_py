# This script talk to gmail to find the answers to questions placed on it network.
# if an email in the inbox of POST_USER_NAME From field = PHONENUMBER@desksms.appspotmail.com
# it will consider it to be a question - it will extract the first line of that email and send it to
# EMAIL_LIST - it will create a timestamp to watermark the transaction.
# with the option --a answer on the command line it will check gmail for subject fields Re:<timestamp>
# The code will then extract the answer and return it to the phone in the from field.

#required modules
import imaplib    #read emails
import smtplib    #send emails
from email.mime.text import MIMEText  #format email text(subject, to, from)
import email      #email functions
import DBD        #database connector
import settings   #settings file
import time       #timestamps


dbd = DBD.DBD()
dbd.connect_db()
dbd.check_update_email()
# my %query;
# use Getopt::Long qw(GetOptions);
# my $verbose = '';
# my $action = 'get';
#
# GetOptions ("a=s" => \$action, "v=i" => \$verbose);  # flag for
# die "You need to specify an action question|answer verbose 0|1 \n" unless $action;
# #for(;;){
# #sleep 60;
# #if ($action =~ /question/){
# 	get_questions();
# #}
# #sleep 60;
# #if ($action =~ /answer/){
# #	get_answers();
# #}
#
# exit;
def get_questions():
    print "[*] Connecting to Gmail to get questions"

    try:
        #log in
        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        imap.login(settings.REC_USER_NAME, settings.REC_PASS)

        #connect to inbox
        imap.select('inbox')

        #get unread email count
        status, unseen_ids = imap.uid('search', None, 'UnSeen')
        if unseen_ids != ['']:
            unseen_ids = unseen_ids[0].split(' ')
            unseen_count = len(unseen_ids)
        else:
            unseen_count = 0

        #get all email count
        status, all_ids = imap.uid('search', None, 'All')
        if all_ids != ['']:
            all_ids = all_ids[0].split(' ')
            mail_count = len(all_ids)
        else:
            mail_count = 0

        print "[*] We have \n\t%s unseen email(s) \n\t%s total email(s)" % (unseen_count, mail_count)

        #for every answered question look for answers
        #returns emails that have desksms.appspotmail.com in the From field
        status, uids = imap.uid('search',None, '(HEADER FROM "*@desksms.appspotmail.com")')
        if uids != ['']:
            uids = uids[0].split(' ')
        else:
            print "[*] No mail from desksms.appspotmail.com"
            return

        for uid in uids:
            status2, flags = imap.uid('fetch', uid, "(FLAGS)")
            if "Seen" in flags[0]:
                print "[-] Warning: Message %s has been seen!" % (uid)
            #print flags
            status, raw_email_body = imap.uid('fetch', uid, "(RFC822)")
            raw_email_body = raw_email_body[0][1]
            sender_email, email_body = get_email_info(raw_email_body)
            email_body = email_body.split('===========================')
            question = email_body[0].strip(" ")
            question = question.replace("\r","")
            question = question.replace("\n","")
            question = question.strip(" ")
            if dbd.question_known(question) > 0:
                print "[-] This question is old. IGNORING"
                continue
            sender_phone = sender_email.split('@')[0]
            print "[+] This message is from %s \n    Question: %s" % (sender_phone, question)
            question_id = send_mail_to_list(0, question, sender_phone)
            if question_id > 0:
                dbd.update_question_DB(question_id,{"question_status":settings.LIVE})
                print "[+] Question is LIVE!"
        imap.close()
    except imaplib.IMAP4.error as e:
         print "[!] Error: %s" % (e.args[0])

def get_answers():
    live_questions_ids = dbd.get_live_questions()

    try:
        #log in
        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        imap.login(settings.REC_USER_NAME, settings.REC_PASS)
        #connect to inbox
        imap.select('inbox')
        for question_id in live_questions_ids:
            question = dbd.get_question_text(question_id)
            print "[*] Looking for answers to Question \'%s\', Question_id: %s" % (question, str(question_id))
            timestamp =  dbd.get_question_timestamp(question_id)
            print "[*] Looking for emails with \'Re: %s\' in the subject" % (str(timestamp))
            query_fields = '(HEADER SUBJECT "Re: '+str(timestamp)+'")'
            status, uids = imap.uid('search',None, query_fields)
            if dbd.is_question_answered(question_id) != -1:
                print "[-] This question has been answered... skipping"
                continue
            for uid in uids:
                #get the body of the email
                if uid == '':
                    print "[-] There are no answers to question \'%s\' yet. Question ID: %s" % (question, question_id)
                    continue
                status, raw_email_body = imap.uid('fetch', str(uid), "(RFC822)")
                raw_email_body = raw_email_body[0][1]
                sender_email, email_body = get_email_info(raw_email_body)
                #Things to get the answer from email response due to HTML formatting in Gmail (haven't checked others)
                first = email_body.index(">")
                last = email_body.index("<",first)
                answer = email_body[first+1:last]
                if "=\r\n" in answer:
                    answer = answer.replace("=\r\n","")
                ####################
                print "[+] Got a reply from %s" % (sender_email)
                print "[+] Question ID = %s \n    The answer to the question \'%s\' is \'%s\'" % (
                                                                        question_id,question,answer)
                #we will now need to send the answer back to the from
                sendto = dbd.get_question_telephone(question_id)
                if sendto == -1:
                    print "[-] There is no telephone for question_id %s" % str(question_id)
                    continue

                answer_id = dbd.add_answer_DB(
                    answer,
                    settings.USE,
                    0,
                    question_id
                )
                send_mail_to_phone(question, answer,sendto)
                if answer_id:
                    dbd.update_question_DB(question_id,{"question_status":settings.UNUSED})
                #delete the email// still have to test
                imap.uid('STORE', uid , '+FLAGS', '(\Deleted)')
                if imap.expunge():
                    print "[+] Gone!"
                #store email, remove from inbox WORKS ON GMAIL, must configure no conversation view
                q = '(BODY \"*'+question+'*\")'
                status2, uid2 = imap.uid('SEARCH', None, q)
                mov, data = imap.uid('STORE', uid2[0] , '+FLAGS', '(\Deleted)')

                imap.expunge()
        imap.close()
    except imaplib.IMAP4.error as e:
         print "[!] Error: %s" % (e.args[0])

def get_time_stamp():
    timestamp = time.ctime() #Max precision: seconds
    return timestamp

def open_phone_log():
    Log = "phone.log"
    try:
        file = open(Log)
        return file
    except IOError as e:
        print "[!] Unable to open logfile"
        return

def get_log_entries():
    ###ASK FOR LOG FORMAT!!!###
    history = open_phone_log()

    # sub get_log_entries {
# 	#get all the log entries
#         my @history = open_phone_log();
#         foreach(@history){
# 		$_ =~  /ID\[(.*)\]PHONE\[(.*)\]COMPLETE\[(.*)\]TIMESTAMP\[(.*)\]TEXT\[(.*)\]FROM\[(.*)\]/;
# 		#print "$1 $2 $3 $4\n";
# 		%{$query{$4}} = (
# 			id => $1,
# 			phone => $2,
# 			complete => $3,
# 			text => $5,
# 			from => $6
# 		);
# 		#print $query{$3}{text}."\n";
#
#
#         }
# }

def open_email_list():
    Log = "email_list.txt"
    try:
        file = open(Log)
        email_list = file.readlines()
        return email_list
    except IOError as e:
        print "[!] Unable to open email list"
        return

def instructions():
    return "\n\nYou are receiving this email from Ye Si's automated HELL\n " \
           "program that she is making Graham code on a lovely day."

def send_mail_to_list(
        timestamp,
        question,
        number
):
    email_addrs = dbd.get_email_list()
    ##get timestamp for this phone_message
    ##this will act as a unique identifier for the message
    timestamp = long(time.time()*100)
    telephone_number_id = dbd.add_telephone_DB(number,settings.USE)
    if not telephone_number_id:
        print("[!] ERROR: No telephone id")
        return -1
    else:
        question_id = dbd.add_question_DB(question,
                                          settings.USE,
                                          telephone_number_id,
                                          0, #no answer yet
                                          timestamp)
        print "[+] Question has timestamp %s" %(timestamp)
    if not question_id:
        print "[!] ERROR: Failed to return a question_id %s" % (question_id)
        return -1

    if dbd.is_question_live(question_id) == settings.LIVE:
        print "[-] Question \'%s\' is already live - no need to send emails" % (question)
        return -1
    try:
        smtp = smtplib.SMTP_SSL('smtp.gmail.com')
        smtp.login(settings.POST_USER_NAME, settings.POST_PASS)
        #Get the question and add instructions
        txt = question + "\n" + instructions()
        #Format to send email
        msg = MIMEText(txt)
        msg['Subject'] = str(timestamp)
        msg['From'] = settings.POST_USER_NAME
        #create email list from all addresses
        email_list = ",".join(email_addrs)
        msg['To'] = email_list
        print "[+] Sending to %s" % (email_addrs)
        smtp.sendmail(settings.POST_USER_NAME, email_addrs, msg.as_string())
        smtp.close()
    except Exception as e:
            print "[!] Error: %s" % (e.args[0])
    return question_id

def send_mail_to_phone(
        question,
        answer,
        sendto_phone
):
    sendto = sendto_phone + "@desksms.appspotmail.com"
    print "[*] Going to send email to %s \n\tQuestion: %s \n\tAnswer: %s" % (sendto, question, answer)
    msg = MIMEText(answer)
    msg['Subject'] = question
    msg['To'] = sendto
    msg['From'] = settings.POST_USER_NAME
    try:
        smtp = smtplib.SMTP_SSL('smtp.gmail.com')
        smtp.login(settings.POST_USER_NAME, settings.POST_PASS)
        smtp.sendmail(settings.POST_USER_NAME, [sendto], msg.as_string() )
        smtp.close()
    except Exception as e:
        print "[-] Error: %s" % (e.args[0])

def get_raw_email():
	password = 'ImiantIndeed'
	me = 'pj14texttonet@gmail.com'

	mail = imaplib.IMAP4_SSL('imap.gmail.com')
	mail.login(me,password)
	#mail.list() #Out: list of "folders" aka labels in gmail account.
	mail.select('inbox') #connect to inbox

	result, data = mail.uid('search',None, "ALL") #get all the unique id's
	uid_list = data[0].split()
	latest_email_uid = uid_list[-1] #get the latest

	result, data = mail.uid('fetch',latest_email_uid, "(RFC822)") # fetch the email body (RFC822) for the given ID
	raw_email = data[0][1]
	return raw_email

def get_email_info(raw_email):
    email_message = email.message_from_string(raw_email)
    sender = email.utils.parseaddr(email_message['From'])[1] #get email from sender
	####################################
    maintype = email_message.get_content_maintype()
    payload = []
    if maintype == 'multipart':
        for part in email_message.get_payload():
            if part.get_content_maintype() == 'text':
                payload = part.get_payload() + "\n***************\n\n\n\n"
    elif maintype == 'text':
        payload = email_message.get_payload()
        payload =  payload.rstrip('\n')
    return sender, payload


if __name__ == '__main__':
    #dbd.init_db()
    #while True:
        #get_questions()
        #time.sleep(5)
        get_answers()
        #time.sleep(5)
    #archive_mail_test()