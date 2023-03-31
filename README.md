# Magic-Link authentication system

A side-car magic-link app which can be used to authenticate a user and pass an encrypted
token to a downstream app.

The flow might be:
1. user request magic link to be sent to email they control
2. magic link exchange and callback to the magic-link app
3. pass encrypted token (fernet/jwt) to downstream app to be decoded and acted upon

Benefits:
1. the magic-link app can be re-used by any app without having a central authority
2. light weight
3. works with any email provider (e.g, mailjet)
4. authorization can be handled in app as necessary

Cons
1. will be running multiple magic-link apps for each Falcon app
2. email.compromised==app.compromised
3. downstream app has to know how to accept/decrypt incoming token


## In this repo

### src

Contains the boilerplate source code for the magic-link app and sample env file.


### src-downstream

Contains the example source for a downstream app to receive the authenticated
token

## TODO

- dockerize
- test
- security review