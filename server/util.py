"""
General Utilities.
"""


def MessageToDict(message):
    """
    https://stackoverflow.com/questions/57203347/how-to-serialize-default-values-in-nested-messages-in-protobuf
    Default inclusive Dict from Protobuf.
    :param message:
    :return:
    """
    messageDict = {}

    for descriptor in message.DESCRIPTOR.fields:
        key = descriptor.name
        value = getattr(message, descriptor.name)

        if descriptor.label == descriptor.LABEL_REPEATED:
            messageList = []

            for subMessage in value:
                if descriptor.type == descriptor.TYPE_MESSAGE:
                    messageList.append(MessageToDict(subMessage))
                else:
                    messageList.append(subMessage)

            messageDict[key] = messageList
        else:
            if descriptor.type == descriptor.TYPE_MESSAGE:
                messageDict[key] = MessageToDict(value)
            else:
                messageDict[key] = value

    return messageDict
