import { Auth } from "rettiwt-auth"

new Auth()
    .getUserCredential({
        email: "account_email",
        userName: "account_username",
        password: "account_password",
    })
    .then((credential) => {
        console.log(credential)
    })
