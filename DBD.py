 # database connector
class DBD:

    FOUND = 1
    NOT_FOUND = 0

    def __init__(self):
        self.dbh = -1
        self.settings = __import__('settings')
        self.MySQLdb = __import__('MySQLdb')

    def connect_db(self):
        # s = " Password: %s\n User: %s\n Database: %s\n" % (self.settings.MYSQL_PASS, self.settings.MYSQL_USER,
        #                                                    self.settings.MYSQL_DB)
        # print (s)
        try:
            self.dbh = self.MySQLdb.connect(
                host="localhost", user=self.settings.MYSQL_USER,
                passwd=self.settings.MYSQL_PASS,
                db=self.settings.MYSQL_DB
                # get_warnings = MYSQL_PRINT_ERROR, #don't report errors via warn
                #raise_on_warnings = MYSQL_RAISE_ERROR #Report errors via die
            )
            print "[+] Connected to database."
        except self.MySQLdb.Error as e:
            print "[*] Error %d: %s" % (e.args[0], e.args[1])
            #print 'ERROR: MSQL:\n Did not connect to (MYSQL){DB}: Maybe MYSQL is not setup'
            return

        return 1


    def check_update_email(self):
        for email in self.settings.email_list:
            self.add_email_DB(email,self.settings.USE)


    def init_db(self):
        try:
            cursor = self.dbh.cursor()
            tables = self.settings.MYSQL_TABLES
            for table in tables:
                print "\n Making table " + table
                cursor.execute(tables[table])
            cursor.close()
        except self.MySQLdb.Error as e:
            print "[*] Error %d: %s" % (e.args[0], e.args[1])


    ## special stuff to disconnect properly from the database.
    ##
    def disconnect_db(self):
        self.dbh.close()
        return
    #
    #
    ## email
    #
    def update_email_DB(
            self,
            email_id,
            keyPairs
    ):
        if email_id is not None:
            try:
                cursor = self.dbh.cursor()
                query_str = "UPDATE email SET "
                for key in keyPairs:
                    query_str = query_str + key + " = \"" + keyPairs[key] + "\" , "
                query_str = query_str[:-2] + " WHERE email_id = " + str(email_id)
                print query_str
                cursor.execute(query_str)
                cursor.close()
                self.dbh.commit()
            except self.MySQLdb.Error as e:
                print "[*] Error %d: %s" % (e.args[0], e.args[1])
        else:
            print "No email_id for update_email_DB " + str(email_id)
        return

    #
    def add_email_DB(
            self,
            email_text,
            email_status_,
    ):
        try:
            cursor = self.dbh.cursor()
            cursor.execute("SELECT email_id FROM email WHERE email_text= \"" + email_text + "\" ")
            r = cursor.fetchone()
            #print r
            if (r is not None):
                #print("[-] Email already exists!")
                email_id = r[0]
                cursor.close()
                return email_id
            else:
                cursor.executemany("""INSERT INTO email
                      (
                          email_text,
                          email_status
                      ) VALUES (%s, %s)""",
                                   [
                                       (email_text,
                                        email_status_)
                                   ]
                )
                self.dbh.commit()
                id = cursor.lastrowid
                cursor.close()
                return id

        except self.MySQLdb.Error as e:
                print "[*] Error %d: %s" % (e.args[0], e.args[1])

    def get_email_list(
            self
    ):
        try:
            dictCursor = self.dbh.cursor(self.MySQLdb.cursors.DictCursor)
            dictCursor.execute(" SELECT * FROM email where email_status = 1")
            resultSet = dictCursor.fetchall()
            #print resultSet
            email_list = []
            for row in resultSet:
                email_list.append(row['email_text'])
            dictCursor.close()

            return email_list
        except self.MySQLdb.Error as e:
                print "[*] Error %d: %s" % (e.args[0], e.args[1])


    # telephones

    def update_telephone_DB(
            self,
            telephone_id,
            keyPairs
    ):
        try:
            if telephone_id is not None:
                cursor = self.dbh.cursor()
                query_str = "UPDATE telephone SET "
                for key in keyPairs:
                    query_str = query_str + key + " = \"" + keyPairs[key] + "\" , "
                query_str = query_str[:-2] + " WHERE telephone_id = " + str(telephone_id)
                print query_str
                cursor.execute(query_str)
                cursor.close()
                self.dbh.commit()
            else:
                print "No question_id for update_telephone_DB " + str(telephone_id)
            return
        except self.MySQLdb.Error as e:
                print "[*] Error %d: %s" % (e.args[0], e.args[1])

    def add_telephone_DB(
            self,
            telephone_text,
            telephone_status_,
        ):
        try:
            cursor = self.dbh.cursor()
            cursor.execute("SELECT telephone_id FROM telephone WHERE telephone_text= \"" + telephone_text + "\" ")
            r = cursor.fetchone()
            #print r
            if (r is not None):
                #print("[-] Telephone already exists!")
                telephone_id = r[0]
                cursor.close()
                return telephone_id
            else:
                cursor.executemany("""INSERT INTO telephone
                       (
                           telephone_text,
                           telephone_status
                       ) VALUES (%s, %s)""",
                                   [
                                       (telephone_text,
                                        telephone_status_)
                                   ]
                )
                self.dbh.commit()
                telephone_id = cursor.lastrowid
                cursor.close()
                return telephone_id
        except self.MySQLdb.Error as e:
                print "[*] Error %d: %s" % (e.args[0], e.args[1])

    #answers
    def update_answer_DB(
            self,
            answer_id,
            keyPairs
    ):
        try:
            if answer_id is not None:
                cursor = self.dbh.cursor()
                query_str = "UPDATE answer SET "
                for key in keyPairs:
                    query_str = query_str + key + " = \"" + keyPairs[key] + "\" , "
                query_str = query_str[:-2] + " WHERE answer_id = " + str(answer_id)
                print query_str
                cursor.execute(query_str)
                cursor.close()
                self.dbh.commit()
            else:
                print "No answer_id for update_answer_DB " + str(answer_id)
            return
        except self.MySQLdb.Error as e:
                print "[*] Error %d: %s" % (e.args[0], e.args[1])

    def add_answer_DB(
            self,
            answer_text,
            answer_status_,
            answer_email_id,
            answer_question_id
    ):
        try:
            cursor = self.dbh.cursor()
            cursor.execute("SELECT answer_id FROM answer WHERE answer_text= \"" + answer_text + "\" ")
            r = cursor.fetchone()
            #print r
            if (r is not None):
                #print("[-] Answer already exists!")
                answer_id = r[0]
                cursor.close()
                return answer_id
            else:
                query = """INSERT INTO answer (
                         answer_text,
                         answer_status,
                         answer_email_id,
                         answer_question_id)
                         VALUES (\"%s\", %d, %d, %d)""" % (answer_text, answer_status_,
                                                               answer_email_id, answer_question_id)
                query = query.strip("\n")
                query = query.strip(" ")
                #print query
                cursor.execute(query)
                self.dbh.commit()
                answer_id = cursor.lastrowid
                cursor.close()
                return answer_id
        except self.MySQLdb.Error as e:
            print "[*] Error %d: %s" % (e.args[0], e.args[1])

    #questions

    def is_question_live(
            self,
            question_id
    ):
        try:
            cursor = self.dbh.cursor()
            cursor.execute("SELECT question_status FROM question WHERE question_id=\"" + str(question_id) + "\"")
            r = cursor.fetchone()
            question_status = -1
            if (r is not None):
                question_status = r[0]
            cursor.close()
            return question_status
        except self.MySQLdb.Error as e:
                print "[*] Error %d: %s" % (e.args[0], e.args[1])

    def is_question_answered(
            self,
            question_id
    ):
        try:
            cursor = self.dbh.cursor()
            cursor.execute("SELECT answer_id FROM answer WHERE answer_question_id=\"" + str(question_id) + "\"")
            r = cursor.fetchone()
            answer_id = -1
            if (r is not None):
                answer_id = r[0]
            cursor.close()
            return answer_id
        except self.MySQLdb.Error as e:
                print "[!] Error %d: %s" % (e.args[0], e.args[1])

    def get_live_questions(
            self,
    ):
        try:
            cursor = self.dbh.cursor()
            cursor.execute("SELECT question_id FROM question WHERE question_status = 2")
            r = cursor.fetchall()
            question_id_ref = []
            if (r is not None):
                for questionId in r:
                    question_id_ref.append(questionId[0])
            cursor.close()
            return question_id_ref
        except self.MySQLdb.Error as e:
                print "[*] Error %d: %s" % (e.args[0], e.args[1])

    def get_question_text(
            self,
            question_id
    ):
        try:
            cursor = self.dbh.cursor()
            cursor.execute("SELECT question_text FROM question WHERE question_id=\"" + str(question_id) + "\"")
            r = cursor.fetchone()
            #print r
            question_text = ''
            if (r is not None):
                question_text = r[0]
            cursor.close()
            return question_text
        except self.MySQLdb.Error as e:
                print "[*] Error %d: %s" % (e.args[0], e.args[1])

    def question_known(
            self,
            question
    ):
        try:
            cursor = self.dbh.cursor()
            cursor.execute("SELECT question_id FROM question WHERE question_text=\"" + str(question) + "\"")
            r = cursor.fetchone()
            question_id = -1
            if (r is not None):
                question_id = r[0]
            cursor.close()
            return question_id
        except self.MySQLdb.Error as e:
                print "[*] Error %d: %s" % (e.args[0], e.args[1])

    def get_question_telephone(
            self,
            question_id
    ):
        try:
            cursor = self.dbh.cursor()
            cursor.execute("SELECT telephone_text FROM telephone, question WHERE question_id=\"" + str(question_id) +
                           "\" AND telephone_id = question_from_telephone_id")
            r = cursor.fetchone()
            telephone = -1
            if (r is not None):
                telephone = r[0]
            cursor.close()
            return telephone
        except self.MySQLdb.Error as e:
                print "[*] Error %d: %s" % (e.args[0], e.args[1])

    def get_question_timestamp(
            self,
            question_id
    ):
        try:
            cursor = self.dbh.cursor()
            cursor.execute("SELECT question_timestamp FROM question WHERE question_id=\"" + str(question_id) + "\"")
            r = cursor.fetchone()
            question_timestamp = ''
            if (r is not None):
                question_timestamp = r[0]
            cursor.close()
            return question_timestamp
        except self.MySQLdb.Error as e:
                print "[*] Error %d: %s" % (e.args[0], e.args[1])
    #
    def update_question_DB(
            self,
            question_id,
            keyPairs
    ):
        if question_id is not None:
            try:
                cursor = self.dbh.cursor()
                query_str = "UPDATE question SET "
                for key in keyPairs:
                    query_str = query_str + key + " = \"" + str(keyPairs[key]) + "\" , "
                query_str = query_str[:-2] + " WHERE question_id = " + str(question_id)
                cursor.execute(query_str)
                cursor.close()
                self.dbh.commit()
            except self.MySQLdb.Error as e:
                print "[*] Error %d: %s" % (e.args[0], e.args[1])
        else:
            print "No question_id for update_question_DB " + str(question_id)
        return

    def add_question_DB(
            self,
            question_text,
            question_status_,
            question_from_telephone_id,
            question_answer_id,
            question_timestamp,
        ):
        try:
            cursor = self.dbh.cursor()
            cursor.execute("SELECT question_id FROM question WHERE question_text= \"" + question_text + "\" ")
            r = cursor.fetchone()
            #print r
            if (r is not None):
                question_id = r[0]
                cursor.close()
                return question_id
            else:
                query = """INSERT INTO question (
                         question_text,
                         question_status,
                         question_from_telephone_id,
                         question_answer_id,
                         question_timestamp)
                         VALUES (\"%s\", %d, %d, %d, %d)""" % (question_text, question_status_,
                                                     question_from_telephone_id, question_answer_id, question_timestamp)
                query = query.strip("\n")
                query = query.strip(" ")
                #print query
                cursor.execute(query)
                cursor.close()
                self.dbh.commit()
                id = cursor.lastrowid
                return id
        except self.MySQLdb.Error as e:
            print "[*] Error %d: %s" % (e.args[0], e.args[1])


    # def main(self):
    #     print "hello"
    #     i = self.dbh.connect_db()
    #     print "blaa " + str(i)
    #     # my code here
    #     #self.init_db()
    #     #self.get_email_list()
    #     #print self.add_question_DB('Who am I?',0,2,1,1234234)
    #     #print self.add_email_DB('Yes it\'s me again, biatch!',1)
    #     #print self.get_question_text(15)
    #     #print self.get_live_questions()
    #     #print self.question_known("Who is them?")
    #     self.update_question_DB(16,{'question_text':'This was question 1','question_status':'1'})
    #     self.disconnect_db()

     #
     # if __name__ == "__main__":
     #     main()



