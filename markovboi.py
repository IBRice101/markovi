import random
import redis


def make_key(user, k):
    """
    Concatenates the user and key with a hyphen in between and returns the resulting bytes object.

        Args:
            user: The user identifier as bytes.
            k: The key as bytes.

        Returns:
            A bytes object that is the concatenation of user and key with a hyphen in between.
    """
    return b'-'.join((user, k))


def parse_key(user, k):
    """
    Extracts the key from a bytes object that contains the user and key concatenated with a hyphen in between.

        Args:
            user: The user identifier as bytes.
            k: The bytes object that contains the user and key concatenated with a hyphen in between.

        Returns:
            A bytes object that is the key extracted from the input bytes object.
    """
    return k[len(user) + 1:]


class MarkovBoi:
    """
       MarkovBoi class generates messages using Markov Chain algorithm. It generates random messages using
       redis database with a chain length of 2.

       Attributes:
           chain_length (int): Length of the chain.
           end_word (str): A special character to mark the end of the message.
           separator (str): A special character used to separate the words in the keys.
           prefix (bytes): The prefix used to create keys in the redis database.
           avg_length (int): The average length of the message to generate.
           all_user (str): A special user identifier used for collecting all the messages.

       Methods:
           __init__(): Initializes the redis client.
           split_message(message): Splits a message into a list of lists of words.
           gen_message(user, seed=None): Generates a message using redis database.
           parse_message(user, message): Parses a message and stores it in the redis database.
   """

    chain_length = 2
    end_word = '\x02'
    separator = '\x01'
    prefix = b'cozy'
    avg_length = 50
    all_user = '000000000000000000'

    def __init__(self):
        """
        Initializes the redis client.
        """
        super(MarkovBoi, self).__init__()
        self.r = redis.Redis()

    def split_message(self, message):
        """
        Splits a message into a list of lists of words.
            Args:
                message (str): The message to split.
            Returns:
                A generator object that yields lists of words.
        """
        words = message.split()

        if len(words) > self.chain_length:
            words.append(self.end_word)
            for i in range(len(words) - self.chain_length):
                yield words[i:i + self.chain_length + 1]

    def gen_message(self, user, seed=None):
        """
        Generates a message using redis database.

            Args:
                user (str): The user for which the message is being generated.
                seed (str): The seed for the message. If None, a random seed is chosen from the redis database.

            Returns:
                A string representing the generated message.
        """
        if seed:
            try:
                key = parse_key(
                    user,
                    random.sample(list(self.r.scan_iter(match=f'*0000-{seed}*')), 1)[0]
                )
            except:
                return '**error:** no messages for that seed :(('
        else:
            key = parse_key(user, self.r.srandmember(user + '-keys'))

        message = []

        for i in range(self.avg_length):
            # get the words from the key
            words = key.split(self.separator.encode())

            # add the word to final message
            message.append(words[0])

            # get next word based on last key
            next_word = self.r.srandmember(make_key(user.encode(), key))

            # these words are fresh :O
            if not next_word:
                break

            # create new key
            key = words[-1] + self.separator.encode() + next_word

        return b' '.join(message).decode()

    def parse_message(self, user, message):
        """
        Parses a message and stores it in the redis database.

            Args:
                user (str): The user who sent the message.
                message (str): The message to parse and store in the redis database.
        """
        for words in self.split_message(message.lower()):
            key = self.separator.join(words[:-1])

            # add the message keys
            self.r.sadd(make_key(user.encode(), key.encode()), words[-1])
            self.r.sadd(make_key(self.all_user.encode(), key.encode()), words[-1])

            # add the keys to the collections of keys
            self.r.sadd(user + '-keys', make_key(user.encode(), key.encode()))
            self.r.sadd(self.all_user + '-keys', make_key(self.all_user.encode(), key.encode()))


if __name__ == '__main__':
    m = MarkovBoi()

    while True:
        m.parse_message("000000000000000000", input('> '))
        print(m.gen_message("000000000000000000"))
