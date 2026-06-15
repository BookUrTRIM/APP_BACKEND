import smtplib
from email.message import EmailMessage
import config


class EmailService:
    @staticmethod
    def send_verification_email(to_email: str, token: str):
        frontend_url = config.FRONTEND_URL
        verify_link = f"{frontend_url.rstrip('/')}/auth/verify-email?token={token}"
        msg = EmailMessage()
        msg['Subject'] = "Confirmez votre adresse email - BookUrTrim"
        msg['From'] = config.SMTP_USER
        msg['To'] = to_email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f8fafc;
                    margin: 0;
                    padding: 0;
                    -webkit-font-smoothing: antialiased;
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background-color: #ffffff;
                    border-radius: 16px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                    border: 1px solid #e2e8f0;
                }}
                .header {{
                    background-color: #4f46e5;
                    padding: 40px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    color: #ffffff;
                    margin: 0;
                    font-size: 28px;
                    font-weight: 800;
                    letter-spacing: -0.5px;
                }}
                .content {{
                    padding: 40px 40px;
                    color: #334155;
                    line-height: 1.6;
                }}
                .content h2 {{
                    color: #0f172a;
                    font-size: 22px;
                    margin-top: 0;
                    margin-bottom: 20px;
                }}
                .button-container {{
                    text-align: center;
                    margin: 40px 0;
                }}
                .button {{
                    background-color: #4f46e5;
                    color: #ffffff !important;
                    text-decoration: none;
                    padding: 14px 32px;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 16px;
                    display: inline-block;
                }}
                .fallback-link {{
                    font-size: 13px;
                    color: #64748b;
                    word-break: break-all;
                    margin-top: 20px;
                }}
                .fallback-link a {{
                    color: #4f46e5;
                }}
                .footer {{
                    background-color: #f1f5f9;
                    padding: 24px;
                    text-align: center;
                    font-size: 13px;
                    color: #64748b;
                    border-top: 1px solid #e2e8f0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>BookUrTrim</h1>
                </div>
                <div class="content">
                    <h2>Bienvenue parmi nous !</h2>
                    <p>Merci de vous être inscrit sur BookUrTrim. Nous sommes ravis de vous compter parmi nous.</p>
                    <p>Pour des raisons de sécurité et pour commencer à utiliser votre compte, veuillez confirmer votre adresse email en cliquant sur le bouton ci-dessous :</p>

                    <div class="button-container">
                        <a href="{verify_link}" class="button">Confirmer mon email</a>
                    </div>

                    <p class="fallback-link">
                        Le bouton ne fonctionne pas ? Copiez-collez ce lien dans votre navigateur :<br>
                        <a href="{verify_link}">{verify_link}</a>
                    </p>
                </div>
                <div class="footer">
                    <p>Si vous n'avez pas créé de compte sur BookUrTrim, vous pouvez ignorer et supprimer cet email en toute sécurité.</p>
                    <p>&copy; 2026 BookUrTrim. Tous droits réservés.</p>
                </div>
            </div>
        </body>
        </html>
        """

        msg.set_content(
            "Veuillez activer votre compte en utilisant le lien envoyé. (Activez l'affichage HTML pour voir ce message correctement)",
            subtype='plain')
        msg.add_alternative(html_content, subtype='html')

        try:
            with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
                server.starttls()
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
                server.send_message(msg)
            print(f"Email de vérification envoyé à {to_email}")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email : {e}")
            print(f"LIEN DE VÉRIFICATION MANUEL : {verify_link}")