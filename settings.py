##USE: import Settings -> use Settings.MYUSER %%imports the module as a whole
##     from Settings import * -> use MYUSER   %%imports the variables and modules
##     Using from <module> import <function, var> you can import only specific variables 

##constants
MYUSER = 'root'
MYDATABASE = 'MAILPHONE'
MYPASS = 'imiant'
#MYPASS = 'YSB40_c'

#fill in your details here
REC_USER_NAME       = 'grahamharw00d50@gmail.com'
REC_PASS        = 'harw00d4007'
REC_MAILHOST        = 'pop.gmail.com' 
POST_USER_NAME      = 'pj14texttonet@gmail.com'
POST_PASS       = 'ImiantIndeed'
POST_MAILHOST       = 'pop.gmail.com'

MYSQL_PASS        = MYPASS 
#MYSQL_DB          = 'dbi:mysql:'+MYDATABASE+';mysql_read_default_file=/etc/mysql/my.cnf'
MYSQL_DB          = MYDATABASE
MYSQL_USER        = MYUSER
MYSQL_PRINT_ERROR = 1
MYSQL_RAISE_ERROR = 1
USE = 1
LIVE = 2
UNUSED  = 0
RECEIVED = 6

# email_list = ['cu301sy@gold.ac.uk']
email_list = ['cu301sy@gold.ac.uk', 'juamps.delavega@gmail.com', 'pj13texttonet@gmail.com']

MYSQL_TABLES = {
	'questions':
		"""create table if not exists question  (
             question_id smallint  not null AUTO_INCREMENT, 
             question_text char(150) not null,
             UNIQUE (question_text),
             question_status smallint unsigned not null,
             question_from_telephone_id smallint unsigned not null,
             question_answer_id smallint unsigned not null,
             question_timestamp BIGINT not null,
             index (question_id)
     ) DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci""",
	
	'answers':
		"""create table if not exists answer  (
             answer_id smallint  not null AUTO_INCREMENT, 
             answer_text char(150) not null,
             UNIQUE (answer_text),
             answer_status smallint unsigned not null,
             answer_email_id  smallint unsigned not null,
             answer_question_id smallint unsigned not null,
             index (answer_id)
      ) DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci""",
	
	'telephone_numbers':
		"""create table if not exists telephone  (
             telephone_id smallint  not null AUTO_INCREMENT, 
             telephone_text char(150) not null,
             UNIQUE (telephone_text),
             telephone_status smallint unsigned not null,
             index (telephone_id)
      ) DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci""",

	'email_list':
		"""create table if not exists email  (
             email_id smallint  not null AUTO_INCREMENT, 
             email_text char(150) not null,
             UNIQUE (email_text),
             email_status smallint unsigned not null,
             index (email_id)
       ) DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci"""

}

#remove the line breaks created by multiline strings
for key in MYSQL_TABLES:
	MYSQL_TABLES[key] = MYSQL_TABLES[key].replace('\n','')

