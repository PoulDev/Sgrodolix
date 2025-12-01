import os
from share.quote import shareQuote
import webbrowser

if __name__ == '__main__':
    #img = shareQuoteWithImage('Dai king!', 'Arthur Schopenhauer', 'Il mondo come volontà e rappresentazione')

    img = shareQuote("a"*1250, 'Fëdor Dostoevskij', 'Memorie del sottosuolo')

    img.save('quote.png')
    os.system('zen-browser quote.png')
