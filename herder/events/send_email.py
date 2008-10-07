import email.mime.text
import email.charset
from email.Header import Header
from email.Utils import parseaddr, formataddr
import smtplib

def send_email(msg_from, recipient_addrs, subject, body,
               header_charset='utf-8', body_charset='utf-8'):
    '''This sends an email.  It uses the msg_from to generate
    the envelope-from as well.'''

    # Validate recipient_addrs
    if not recipient_addrs:
        return
    for addr in recipient_addrs:
        assert '@' in addr

    # Python Unicode sanity c/o http://mg.pov.lt/blog/unicode-emails-in-python.html

    msg_from = unicode(msg_from)

    # Prepare SMTP-level sender and recipient
    sender_name, sender_addr = parseaddr(
        '"Translation System" <herder-bounces@localhost>')

    # We must always pass Unicode strings to Header, otherwise it will
    # use RFC 2047 encoding even on plain ASCII strings.
    sender_name = str(Header(unicode(sender_name), header_charset))
    # no recipient_name in the header

    # Make sure email addresses do not contain non-ASCII
    # characters
    # (FIXME: This could blow up at runtime if we don't
    # assert this at other layers, like the DB!)
    sender_addr = unicode(sender_addr).encode('ASCII')

    # Create the message ('plain' stands for Content-Type: text/plain)
    charset_obj = email.charset.Charset('utf-8')
    charset_obj.header_encoding = email.charset.QP
    charset_obj.body_encoding = email.charset.QP

    msg = email.mime.text.MIMEText(body.encode(body_charset), 'plain')
    # Message class computes the wrong type from MIMEText constructor,
    # which does not take a Charset object as initializer. Reset the
    # encoding type to force a new, valid evaluation
    del msg['Content-Transfer-Encoding'] # base64 by default, wtf
    msg.set_charset(charset_obj) # QP utf-8, ahhh :-)
    
    msg['From'] = formataddr( (sender_name, sender_addr) )
    # Leave "To:" blank
    msg['Subject'] = Header(unicode(subject), header_charset)

    server = smtplib.SMTP('localhost') # hard-coded
    server.sendmail(sender_addr, recipient_addrs, msg.as_string())
    server.quit()
