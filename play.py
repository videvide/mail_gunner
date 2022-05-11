import csv
import time
import boto3

CHARSET = "UTF-8"

ses_client = boto3.client("ses", region_name="eu-north-1")


def create_email_message(name):
    return f"""Hej, {name}!

Detta är en idé som jag känner mig tvingad att dela. Förhoppningen är att den ska ge dig nöjdare köpare, varmare rekommendationer och ett tillskott på kontot.

Du har bättre koll men jag har en känsla av att många köpare letar efter passande konst till deras ny hem. Istället för att de ska spendera tid på att leta efter konst kan de få den skräddarsydd genom min smidiga tjänst. 

Du får gärna kolla in hemsidan där det finns exempel på hur processen går till och recensioner från tidigare beställare. Om du vill rekommendera mig är du välkommen att återkoppla för att diskutera ett bra upplägg.

Önskar dig en fortsatt bra dag.

Vide

neilmatsvide.se"""


def send_plain_email(email, name):
    response = ses_client.send_email(
        Destination={
            "ToAddresses": [email],
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


emails_names = set()

with open("mails.csv", "r") as file:
    csvreader = csv.reader(file)
    header = next(csvreader)
    for row in csvreader:
        emails_names.add(tuple(row))

print(emails_names)

while len(emails_names):
    count = 0
    while count < 13:
        try:
            email, name = emails_names.pop()
            print(count, email, name)
            send_plain_email(email, name)
            count += 1
        except:
            break
    time.sleep(1)
