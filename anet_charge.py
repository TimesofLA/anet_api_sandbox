"""
Charge a credit card
"""

import importlib
import os
import sys
import random
from faker import Faker # for fake gANenerated information
fake = Faker()
from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController

CONSTANTS = importlib.import_module('constants')


def charge_credit_card(amount):
    """
    Charge a credit card
    """

    # Create a merchantAuthenticationType object with authentication details
    # retrieved from the constants file
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = CONSTANTS.apiLoginId
    merchantAuth.transactionKey = CONSTANTS.transactionKey
    

    # Create the payment data for a credit card
    creditCard = apicontractsv1.creditCardType()
    card_types = ['visa','discover','mastercard', 'jcb']
    creditCard.cardNumber = fake.credit_card_number(card_type=random.choice(card_types))
    creditCard.expirationDate = fake.credit_card_expire()
    creditCard.cardCode = fake.credit_card_security_code()

    # Add the payment data to a paymentType object
    payment = apicontractsv1.paymentType()
    payment.creditCard = creditCard
    
    

    # Create order information
    order = apicontractsv1.orderType()
    order.invoiceNumber = str(random.randint(1000,3000))
    order.description = fake.bs()

    # Set the customer's Bill To address
    customerAddress = apicontractsv1.customerAddressType()
    customerAddress.firstName = fake.first_name()
    customerAddress.lastName = fake.last_name()
    customerAddress.company = fake.bs()
    customerAddress.address = fake.street_address()
    customerAddress.city = fake.city()
    customerAddress.state = fake.address().split()[-1].split()[0]
    customerAddress.zip = fake.postalcode_in_state()
    customerAddress.country = fake.country()
    customerAddress.phoneNumber = fake.phone_number()
    

    # Set the customer's identifying information
    customerData = apicontractsv1.customerDataType()
    customerData.type = "individual"
    customerData.id = fake.upc_e()
    customerData.email = fake.email()

    # Add values for transaction settings
    duplicateWindowSetting = apicontractsv1.settingType()
    duplicateWindowSetting.settingName = "duplicateWindow"
    duplicateWindowSetting.settingValue = "600"
    settings = apicontractsv1.ArrayOfSetting()
    settings.setting.append(duplicateWindowSetting)

    # setup individual line items
    line_item_1 = apicontractsv1.lineItemType()
    line_item_1.itemId = "12345"
    line_item_1.name = "first"
    line_item_1.description = fake.catch_phrase()
    line_item_1.quantity = "2"
    line_item_1.unitPrice = "12.95"
    line_item_2 = apicontractsv1.lineItemType()
    line_item_2.itemId = "67890"
    line_item_2.name = "second"
    line_item_2.description = fake.catch_phrase()
    line_item_2.quantity = "3"
    line_item_2.unitPrice = "7.95"
    line_item_3 = apicontractsv1.lineItemType()
    line_item_3.itemId = "ID num goes here"
    line_item_3.name = "third"
    line_item_3.description = fake.catch_phrase()
    line_item_3.quantity = "12"
    line_item_3.unitPrice = "100.00"


    # build the array of line items
    line_items = apicontractsv1.ArrayOfLineItem()
    line_items.lineItem.append(line_item_1)
    line_items.lineItem.append(line_item_2)
    line_items.lineItem.append(line_item_3)

    # Create a transactionRequestType object and add the previous objects to it.
    transactionrequest = apicontractsv1.transactionRequestType()
    transactionrequest.transactionType = "authCaptureTransaction"
    transactionrequest.amount = amount
    transactionrequest.payment = payment
    transactionrequest.order = order
    transactionrequest.billTo = customerAddress
    transactionrequest.customer = customerData
    transactionrequest.transactionSettings = settings
    transactionrequest.lineItems = line_items
    

    # Assemble the complete transaction request
    createtransactionrequest = apicontractsv1.createTransactionRequest()
    createtransactionrequest.merchantAuthentication = merchantAuth
    createtransactionrequest.refId = "1234-3432"
    createtransactionrequest.transactionRequest = transactionrequest
    # Create the controller
    createtransactioncontroller = createTransactionController(
        createtransactionrequest)
    createtransactioncontroller.execute()

    response = createtransactioncontroller.getresponse()

    if response is not None:
        # Check to see if the API request was successfully received and acted upon
        if response.messages.resultCode == "Ok":
            # Since the API request was successful, look for a transaction response
            # and parse it to display the results of authorizing the card
            if hasattr(response.transactionResponse, 'messages') is True:
                print(
                    'Successfully created transaction with Transaction ID: %s'
                    % response.transactionResponse.transId)
                print('Transaction Response Code: %s' %
                      response.transactionResponse.responseCode)
                print('Message Code: %s' %
                      response.transactionResponse.messages.message[0].code)
                print('Description: %s' % response.transactionResponse.
                      messages.message[0].description)
            else:
                print('Failed Transaction.')
                if hasattr(response.transactionResponse, 'errors') is True:
                    print('Error Code:  %s' % str(response.transactionResponse.
                                                  errors.error[0].errorCode))
                    print(
                        'Error message: %s' %
                        response.transactionResponse.errors.error[0].errorText)
        # Or, print errors if the API request wasn't successful
        else:
            print('Failed Transaction.')
            if hasattr(response, 'transactionResponse') is True and hasattr(
                    response.transactionResponse, 'errors') is True:
                print('Error Code: %s' % str(
                    response.transactionResponse.errors.error[0].errorCode))
                print('Error message: %s' %
                      response.transactionResponse.errors.error[0].errorText)
            else:
                print('Error Code: %s' %
                      response.messages.message[0]['code'].text)
                print('Error message: %s' %
                      response.messages.message[0]['text'].text)
    else:
        print('Null Response.')

    return response


if (os.path.basename(__file__) == os.path.basename(sys.argv[0])):
        charge_credit_card(CONSTANTS.amount)


# if __name__ == "__main__":
#     for _ in range(100):
#         charge_credit_card(CONSTANTS.amount)
        