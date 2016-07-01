from validate_email import validate_email


def fetch_mail(here):
    name, mail = here.split('<')
    return (name, mail.rstrip('>'))


def case_pair(decode):
    if len(decode) == 2:
            mail = decode[1][0].strip('<>')
            if validate_email(mail):
                return (mail, unicode(decode[0][0], encoding=decode[0][1]))


def case_single(decode):
    if validate_email(decode[0][0]):
        if decode[0][0]:
            return (decode[0][0], None)


def case_fetch_str(decode):
    name, mail = fetch_mail(decode[0][0])
    if validate_email(mail):
        return (mail, name.strip())


def if_reply_available(email_address):
    '''
    We won`t reply to those addressee, who has 'noreply' in address.
    Aslo we won`t reply to robots
    '''
    e = email_address.lower()
    if 'no-reply' in e or 'noreply' in e:
        return False

    noreplies = ['accounts.google.com', 'plus.google.com']
    for n in noreplies:
        if e.endswith(n):
            return False

    return True
