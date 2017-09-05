import imaplib
import email
from bs4 import BeautifulSoup
import code

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('X', 'X')
print mail.list()
mail.select('inbox')

result, email_list = mail.uid('search', None, "UNSEEN")
#result, email_list = mail.uid('search', None, "ALL")
print 'search: ', email_list

for l in email_list[0].split():
    print l
    result, data = mail.uid( 'fetch', l, '(RFC822)' ) #get email '2'

    email_message = email.message_from_string( data[0][1] )
    print 'Sender : ', email_message['From']
    print 'Subject : ', email_message['Subject']
    print 'Received  : ', email_message['Received']
    #print email_message.keys()


    for part in email_message.walk():
         print part.get_content_type()
         if part.get_content_type() == "text/html": # ignore attachments/html
               body = part.get_payload(decode=True)
               #print body

               soup = BeautifulSoup(body, 'lxml')
               table = soup.find( "table")
               all_tr = table.find_all( 'tr', recursive=False )
               for tr in all_tr:
                   divs = tr.find_all( 'div', recursive=True)
                   print len(divs)
                   if len(divs) >= 5:

                       a_ = divs[0].find('a')
                       print a_.text
                       #code.interact( local=locals() )
