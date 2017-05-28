import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError

from django.conf import settings

import requests
from twilio.rest import Client

from .exceptions import SendSMSError


class BaseSMSBackend:
    """
    Base class for sms backend implementations
    Subclasses must at least overwrite send_messages().

    """

    def send_message(self, sms):
        raise NotImplementedError('subclasses of BaseSMSBackend must override send_message() method')


class DummyBackend(BaseSMSBackend):

    def send_message(self, sms):
        pass


class TwilioBackend(BaseSMSBackend):

    def send_message(self, sms):
        client = Client(settings.TWILIO_ACCOUNT_NUMBER,
                        settings.TWILIO_AUTH_TOKEN)

        client.api.account.messages.create(from_=settings.TWILIO_FROM_NUMBER,
                                           to=sms.to,
                                           body=sms.message)


class NadyneBackend(BaseSMSBackend):

    def send_message(self, sms):
        params = {
            'user': settings.NADYNE_USER,
            'pwd': settings.NADYNE_PASSWORD,
            'sender': settings.NADYNE_SENDER,
            'msisdn': sms.to,
            'message': sms.message,
            'description': sms.description
        }
        response = requests.get("http://apitoken.nadyne.com/sms.php", params=params)
        if response.status_code == 200:
            status = ET.fromstring(response.content).find('Status').text
            if status != "SENT":
                raise SendSMSError(status)
        else:
            raise SendSMSError("Network Error")