import csv
import sys
import logging
import time
import boto3

CHARSET = "UTF-8"
LOG_FORMAT = "%(levelname)s %(asctime)s %(message)s"
SUCCESFUL = "successful_emails.csv"
UNSUCCESFUL = "unsuccessful_emails.csv"

logging.basicConfig(filename="logfile.log", format=LOG_FORMAT, level=logging.INFO)
logger = logging.getLogger()

ses_client = boto3.client("ses", region_name="eu-north-1")

print("Welcome to Email Mayhem ")
email_file = input("Enter email file name: ")


def create_email_message(name):
    return f"""Hej, {name}!

Detta är en idé som jag känner mig tvingad att dela. Förhoppningen är att den ska ge dig nöjdare kunder, varmare rekommendationer och ett tillskott på kontot.

Du har bättre koll men jag har en känsla av att många köpare letar efter passande konst till deras ny hem. Istället för att de ska spendera tid på att leta efter konst kan de få den skräddarsydd genom min smidiga tjänst. 

Du får gärna kolla in hemsidan där det finns exempel på hur processen går till och recensioner från tidigare beställare. Om du vill rekommendera mig är du välkommen att återkoppla för att diskutera ett bra upplägg.

Önskar dig en fortsatt trevlig kväll.

Vide

neilmatsvide.se"""


def write_email_address_to_file(file_name, email):
    with open(file_name, "a") as f:
        f.write(f"\n{email}")


def send_plain_email(email, name):
    response = ses_client.send_email(
        Destination={
            "ToAddresses": [
                email,
            ],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": CHARSET,
                    "Data": create_email_message(name),
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data": "Detta kan vara intressant för dig och dina köpare",
            },
        },
        Source="Vide Krajnc <vide@neilmatsvide.se>",
    )

    return response


def send_emails(emails_names):
    while len(emails_names):
        count = 0
        # keep track of count to stay under sending treshold
        while count < 13:
            try:
                email, name = emails_names.pop()
                try:
                    print(count, email, name)
                    response = send_plain_email(email, name)

                    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                        status_code = response["ResponseMetadata"]["HTTPStatusCode"]
                        logger.warning(f"Status_code: {status_code} | {email}")
                        print(f"Status_code: {status_code} | {email}")
                        write_email_address_to_file(UNSUCCESFUL, email)

                    else:
                        logger.info(f"Successfully sent to: {email}")
                        print(f"Successfully sent to: {email}")
                        write_email_address_to_file(SUCCESFUL, email)

                except ses_client.exceptions.MessageRejected as error:
                    logger.warning(f"{error} | {email}")
                    print(f"{error} | {email}")
                    write_email_address_to_file(UNSUCCESFUL, email)

                except ses_client.exceptions.MailFromDomainNotVerifiedException as error:
                    logger.critical(f"SYS EXIT | {error} | {email}")
                    sys.exit()

                except ses_client.exceptions.AccountSendingPausedException as error:
                    logger.critical(f"SYS EXIT | {error} | {email}")
                    sys.exit()
                # increment count to stay under treshold
                count += 1
            except:
                break
        time.sleep(1)


emails_names = set()

with open(f"{email_file}.csv", "r") as file:
    csvreader = csv.reader(file)
    header = next(csvreader)
    for row in csvreader:
        emails_names.add(tuple(row))

send_emails(emails_names)
