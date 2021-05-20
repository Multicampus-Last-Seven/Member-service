from random import randint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

def get_new_password():
    chars = [[str(i) for i in range(10)]]
    chars.append(['!', '@', '#', '$', '%', '^', '&', '*'])
    chars.append([chr(i) for i in range(ord('a'), ord('z')+1)])
    pw = ''

    for _ in range(10):
        k = randint(0, len(chars)-1)
        th = randint(0, len(chars[k])-1)
        pw += chars[k][th]
    
    return pw