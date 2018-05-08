PHONY: user

USER ?= oz123
MAIL ?= oz.tiram@noris.de

user:
	curl --header "Content-Type: application/json" \
	--request POST \
	--data '{"name":"${USER}","password":"s3kr3t", "email": "${MAIL}"}' \
	http://localhost:8080/usr/
