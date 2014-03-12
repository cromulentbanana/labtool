#!/usr/bin/env python
#
# Dan Levin <dan@net.t-labs.tu-berlin.de>
# The very first acceptance test

from splinter import Browser

def testLoginWithWrongCredentialsFails():
    browser = Browser()
    browser.visit('http://127.0.0.1:8000')
    browser.fill_form({'username': 'admin'})
    browser.fill_form({'password': 'falsepw'})
    browser.find_by_value('Anmelden').click()

    if browser.is_text_present('Your login credentials are incorrect'):
        print "Test passed"
    else:
        print "Test failed"

    browser.quit()

def testLoginWithCredentialsSucceeds():
    browser = Browser()
    browser.visit('http://127.0.0.1:8000')
    browser.fill_form({'username': 'admin'})
    browser.fill_form({'password': 'admin'})
    browser.find_by_value('Anmelden').click()

    if browser.is_text_present('Your login credentials are incorrect'):
        print "Test failed"
    else:
        print "Test passed"

    browser.quit()

testLoginWithCredentialsSucceeds()
testLoginWithWrongCredentialsFails()

