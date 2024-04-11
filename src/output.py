import datetime


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class c_print:
    # If called without static method, simply print the string
    @staticmethod
    def __call__(**print_stringss):
        # print the strings
        print(**print_stringss)

    @staticmethod
    def time(*print_strings):
        # add timestamp to print statements
        print(
            f"[{datetime.datetime.now().strftime('%H:%M:%S:%f')[:-3]}]", *print_strings
        )

    @staticmethod
    def ok(*print_strings):
        # print success message
        c_print.time(Colors.OKGREEN, *print_strings, Colors.ENDC)

    @staticmethod
    def blue(*print_strings):
        # print info message
        c_print.time(Colors.OKBLUE, *print_strings, Colors.ENDC)

    @staticmethod
    def cyan(*print_strings):
        # print info message
        c_print.time(Colors.OKCYAN, *print_strings, Colors.ENDC)

    @staticmethod
    def warn(*print_strings):
        # print warning message
        c_print.time(Colors.WARNING, *print_strings, Colors.ENDC)

    @staticmethod
    def fail(*print_strings):
        # print error message
        c_print.time(Colors.FAIL, *print_strings, Colors.ENDC)
