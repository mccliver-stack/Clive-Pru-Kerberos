# Interview Notes

## Kerberos Authentication
When a user logs into a domain-joined machine, they enter their username and password. The client sends a request to the domain controller, which acts as the Key Distribution Center. The domain controller validates the credentials and, if successful, issues a Ticket Granting Ticket (TGT). The user then uses that TGT to request service tickets for specific resources, like file servers or applications. Those service tickets are presented to the target systems to gain access without sending the password again. This allows secure, ticket-based authentication within Active Directory.

## Hybrid Authentication (ADFS + Entra ID)
When a user tries to access a cloud application, they are already authenticated on their domain-joined machine using Kerberos. The request goes to Entra ID, which detects a federated domain and redirects the user to ADFS. ADFS authenticates the user against Active Directory and issues a SAML token containing claims. This token is sent back to Entra ID, which then generates an access token for the application. This enables Single Sign-On so the user does not need to enter credentials again.

## Kerberos vs SAML
Kerberos tickets are used for authentication within an Active Directory environment and are issued by the domain controller. They allow secure access to internal resources without repeatedly sending the password. SAML tokens are used for federated authentication, typically for web and cloud applications. They are issued by identity providers like ADFS and contain claims about the user. Kerberos is used internally, while SAML is used for external or cloud-based authentication.
